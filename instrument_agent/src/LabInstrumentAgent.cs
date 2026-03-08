using System.Net.Http.Json;
using System.Text.Json;

namespace InstrumentAgent;

public sealed class LabInstrumentAgent : IInstrumentAgent
{
    public string InstrumentId { get; }
    public string Name { get; }

    private readonly AgentConfig _config;
    private readonly HttpClient _http;
    private readonly ILogger _logger;
    private CancellationTokenSource? _cts;

    public LabInstrumentAgent(AgentConfig config, HttpClient http, ILogger logger)
    {
        _config = config;
        _http = http;
        _logger = logger;
        InstrumentId = config.InstrumentId;
        Name = config.Name;
    }

    public async Task StartAsync(CancellationToken ct)
    {
        _cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        var token = _cts.Token;

        _logger.Log($"Agent '{Name}' ({InstrumentId}) starting. Backend: {_config.BackendUrl}");

        while (!token.IsCancellationRequested)
        {
            await SendHeartbeatAsync(token);
            await PollCommandsAsync(token);
            await Task.Delay(TimeSpan.FromSeconds(_config.HeartbeatIntervalSeconds), token);
        }
    }

    public async Task StopAsync()
    {
        _logger.Log($"Agent '{Name}' stopping.");
        _cts?.Cancel();
        await Task.CompletedTask;
    }

    // ── private ──────────────────────────────────────────────────────────────

    private async Task SendHeartbeatAsync(CancellationToken ct)
    {
        try
        {
            var payload = new { instrument_id = InstrumentId, name = Name, status = "online" };
            var resp = await _http.PostAsJsonAsync($"{_config.BackendUrl}/api/instruments/heartbeat", payload, ct);
            _logger.Log($"Heartbeat → {(int)resp.StatusCode}");
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            _logger.Log($"Heartbeat failed: {ex.Message}");
        }
    }

    private async Task PollCommandsAsync(CancellationToken ct)
    {
        try
        {
            var resp = await _http.GetAsync(
                $"{_config.BackendUrl}/api/instruments/{InstrumentId}/commands", ct);

            if (!resp.IsSuccessStatusCode)
                return;

            var commands = await resp.Content.ReadFromJsonAsync<List<InstrumentCommand>>(
                cancellationToken: ct) ?? [];

            foreach (var cmd in commands)
                await ExecuteCommandAsync(cmd, ct);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            _logger.Log($"Command poll failed: {ex.Message}");
        }
    }

    private Task ExecuteCommandAsync(InstrumentCommand cmd, CancellationToken ct)
    {
        _logger.Log($"Executing command: {cmd.Type} (id={cmd.Id})");

        // TODO: dispatch to real instrument hardware
        return Task.CompletedTask;
    }
}

public sealed record InstrumentCommand(string Id, string Type, JsonElement? Payload);
