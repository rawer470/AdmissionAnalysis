using Microsoft.AspNetCore.Mvc;
using WebApp.Models.ViewModels;
using WebApp.Services;

namespace WebApp.Controllers;

public class AdmissionController : Controller
{
    private readonly ImportService _import;

    public AdmissionController(ImportService import) => _import = import;

    [HttpGet]
    public IActionResult Index()
    {
        var vm = new CsvStatsVm
        {
            Deleted = (int)(TempData["Deleted"] ?? 0),
            Inserted = (int)(TempData["Inserted"] ?? 0),
            Updated = (int)(TempData["Updated"] ?? 0),
            SnapshotRows = (int)(TempData["SnapshotRows"] ?? 0)
        };
        return View(vm);
    }

    /// <summary>
    /// GET: страница для загрузки csv-файлов
    /// </summary>
    /// <returns></returns>
    [HttpGet]
    public IActionResult UploadCsv() => View();

    /// <summary>
    /// POST: пользователь отправляет 4 файла за день
    /// </summary>
    /// <param name="model"></param>
    /// <param name="ct"></param>
    /// <returns></returns>
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> UploadCsv(UploadCsvVm model, CancellationToken ct)
    {
        if (model.Pm is null || model.Ivt is null || model.Itss is null || model.Ib is null)
            return BadRequest("Need 4 files: pm, ivt, itss, ib");

        var dataFromCsv = await _import.ImportDayAsync(model.Pm, model.Ivt, model.Itss, model.Ib, ct);
        TempData["Deleted"] = dataFromCsv.deleted;
        TempData["Inserted"] = dataFromCsv.inserted;
        TempData["Updated"] = dataFromCsv.updated;
        TempData["SnapshotRows"] = dataFromCsv.snapshotRows;
        return RedirectToAction(nameof(Index));
    }

    // Для перехода на Политику Конфедециальности
    public IActionResult Privacy() => View(); 
}
