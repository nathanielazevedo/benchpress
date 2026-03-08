namespace InstrumentAgent;

/// <summary>
/// Contract for a lab instrument agent.
/// Implementations connect to the backend, send heartbeats,
/// and execute commands dispatched to this instrument.
/// </summary>
public interface IInstrumentAgent
{
    /// <summary>Unique identifier for this instrument on the network.</summary>
    string InstrumentId { get; }

    /// <summary>Human-readable label shown in the UI.</summary>
    string Name { get; }

    /// <summary>Start the agent loop (heartbeat + command polling).</summary>
    Task StartAsync(CancellationToken ct);

    /// <summary>Gracefully stop the agent loop.</summary>
    Task StopAsync();
}
