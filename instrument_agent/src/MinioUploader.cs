using Minio;
using Minio.DataModel.Args;

namespace InstrumentAgent;

public sealed class MinioUploader
{
    private readonly IMinioClient _client;
    private readonly string _bucket;
    private readonly string _instrumentId;
    private readonly ILogger _logger;

    public MinioUploader(AgentConfig config, ILogger logger)
    {
        _bucket       = config.MinioBucket;
        _instrumentId = config.InstrumentId;
        _logger       = logger;

        _client = new MinioClient()
            .WithEndpoint(config.MinioEndpoint)
            .WithCredentials(config.MinioAccessKey, config.MinioSecretKey)
            .WithSSL(config.MinioSsl)
            .Build();
    }

    public async Task EnsureBucketAsync(CancellationToken ct = default)
    {
        var exists = await _client.BucketExistsAsync(
            new BucketExistsArgs().WithBucket(_bucket), ct);

        if (!exists)
        {
            await _client.MakeBucketAsync(
                new MakeBucketArgs().WithBucket(_bucket), ct);
            _logger.Log($"Created bucket '{_bucket}'");
        }
    }

    public async Task UploadFileAsync(string filePath, CancellationToken ct = default)
    {
        // Object key: {instrumentId}/{date}/{filename}
        // e.g. instrument-001/2026-03-09/run_output.csv
        var now        = DateTime.UtcNow;
        var date       = now.ToString("yyyy-MM-dd");
        var fileName   = Path.GetFileName(filePath);
        var objectName = $"{_instrumentId}/{date}/{fileName}";

        var contentType = GuessContentType(filePath);

        // User metadata stored alongside the object
        var metadata = new Dictionary<string, string>
        {
            ["instrument-id"]      = _instrumentId,
            ["uploaded-at"]        = now.ToString("o"),   // ISO 8601
            ["original-filename"]  = fileName,
        };

        await _client.PutObjectAsync(new PutObjectArgs()
            .WithBucket(_bucket)
            .WithObject(objectName)
            .WithFileName(filePath)
            .WithContentType(contentType)
            .WithHeaders(metadata), ct);

        _logger.Log($"Uploaded '{fileName}' → {_bucket}/{objectName}");
    }

    private static string GuessContentType(string path) =>
        Path.GetExtension(path).ToLowerInvariant() switch
        {
            ".csv"  => "text/csv",
            ".xml"  => "application/xml",
            ".json" => "application/json",
            ".txt"  => "text/plain",
            ".pdf"  => "application/pdf",
            _       => "application/octet-stream",
        };
}
