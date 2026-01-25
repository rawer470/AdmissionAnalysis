namespace WebApp.Models.ViewModels;

public class CsvStatsVm
{
    public int Inserted { get; set; }
    public int Updated { get; set; }
    public int Deleted { get; set; }
    public int SnapshotRows { get; set; }
}