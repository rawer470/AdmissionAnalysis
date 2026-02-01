using WebApp.Data.Entities;

namespace WebApp.Models.DTO;

/// <summary>
/// DTO-модель-дубляж ApplicantsCurrent для фронта
/// </summary>
public sealed class VisualizeItemDto
{
    public int ApplicantId { get; set; }
    public ProgramCode Program { get; set; }
    public bool Consent { get; set; }
    public int Priority { get; set; }
    public int PhysicsIct { get; set; }
    public int Russian { get; set; }
    public int Math { get; set; }
    public int Individual { get; set; }
    public int Total { get; set; }
}
