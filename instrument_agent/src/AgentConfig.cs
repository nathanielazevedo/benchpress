namespace InstrumentAgent;

public sealed class AgentConfig
{
    public string BackendUrl { get; init; } = "http://localhost:8000";
    public string InstrumentId { get; init; } = Environment.MachineName;
    public string Name { get; init; } = "Lab Instrument";
    public int HeartbeatIntervalSeconds { get; init; } = 30;
}
