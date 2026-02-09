namespace WebApp.Models.ViewModels;

public class UploadCsvVm
{
    public string DateFolder { get; set; } = "01";
    public IFormFile Pm { get; set; }
    public IFormFile Ivt { get; set; }
    public IFormFile Itss { get; set; }
    public IFormFile Ib { get; set; }
}
