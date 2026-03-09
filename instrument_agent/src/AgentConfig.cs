namespace InstrumentAgent;

public sealed record AgentConfig
{
    public string BackendUrl { get; init; } = "http://localhost:8000";
    public string InstrumentId { get; init; } = Environment.MachineName;
    public string Name { get; init; } = "Lab Instrument";
    public int HeartbeatIntervalSeconds { get; init; } = 30;

    // Lab / company association — empty means prompt on startup
    public string LabId { get; init; } = "";
    public string CompanyId { get; init; } = "";

    // File watcher — empty means prompt on startup
    public string WatchPath { get; init; } = "";

    // MinIO / S3
    public string MinioEndpoint { get; init; } = "localhost:9000";
    public string MinioAccessKey { get; init; } = "minioadmin";
    public string MinioSecretKey { get; init; } = "minioadmin";
    public string MinioBucket { get; init; } = "instrument-data";
    public bool MinioSsl { get; init; } = false;
}
