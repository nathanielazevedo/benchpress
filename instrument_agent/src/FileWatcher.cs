namespace InstrumentAgent;

/// <summary>
/// Watches a directory for new or changed files and fires OnFileReady
/// once the file is fully written (no longer locked by the writer).
/// </summary>
public sealed class FileWatcher : IDisposable
{
    public event Func<string, CancellationToken, Task>? OnFileReady;

    private readonly FileSystemWatcher _watcher;
    private readonly ILogger _logger;
    private readonly CancellationToken _ct;

    // Debounce: track files we've already queued to avoid duplicate events
    private readonly HashSet<string> _pending = [];
    private readonly object _lock = new();

    public FileWatcher(string path, ILogger logger, CancellationToken ct)
    {
        _logger = logger;
        _ct = ct;

        _watcher = new FileSystemWatcher(path)
        {
            NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite,
            IncludeSubdirectories = false,
            EnableRaisingEvents = true,
        };

        _watcher.Created += OnChanged;
        _watcher.Changed += OnChanged;

        _logger.Log($"Watching '{path}' for new files...");
    }

    private void OnChanged(object _, FileSystemEventArgs e)
    {
        if (string.IsNullOrEmpty(e.FullPath)) return;

        lock (_lock)
        {
            if (!_pending.Add(e.FullPath)) return; // already queued
        }

        // Fire-and-forget: wait for the file to be released then raise event
        _ = Task.Run(() => WaitAndRaiseAsync(e.FullPath), _ct);
    }

    private async Task WaitAndRaiseAsync(string filePath)
    {
        // Poll until the file is no longer locked (instrument has finished writing)
        for (int attempt = 0; attempt < 20; attempt++)
        {
            await Task.Delay(500, _ct);
            if (IsFileReady(filePath)) break;
        }

        lock (_lock) { _pending.Remove(filePath); }

        if (OnFileReady is not null)
        {
            try { await OnFileReady(filePath, _ct); }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                _logger.Log($"Error handling file '{Path.GetFileName(filePath)}': {ex.Message}");
            }
        }
    }

    private static bool IsFileReady(string path)
    {
        try
        {
            using var fs = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.None);
            return true;
        }
        catch (IOException)
        {
            return false;
        }
    }

    public void Dispose() => _watcher.Dispose();
}
