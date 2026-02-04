using Microsoft.AspNetCore.Mvc;
using WebApp.Models.ViewModels;
using WebApp.Services;

namespace WebApp.Controllers;

public class AdmissionController : Controller
{
    private readonly ImportService _import;
    private readonly AnalysisService _analysis;

    public AdmissionController(ImportService import, AnalysisService analysis)
    {
        _import = import;
        _analysis = analysis;
    }

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

        if (string.IsNullOrEmpty(model.DateFolder))
            model.DateFolder = "01";

        // 1. Загружаем CSV в БД и сохраняем в uploads
        var dataFromCsv = await _import.ImportDayAsync(model.DateFolder, model.Pm, model.Ivt, model.Itss, model.Ib, ct);

        // 2. Вызываем Python API для анализа и создания stats.json в reports
        try
        {
            await _analysis.AnalyzeAsync(model.DateFolder);
            TempData["AnalysisSuccess"] = true;

            // 3. Генерируем PDF отчет и PNG график (автоматически находит все доступные отчеты)
            await _analysis.GeneratePdfReportAsync(null, model.DateFolder);
            TempData["PdfGenerated"] = true;
        }
        catch (Exception ex)
        {
            TempData["AnalysisError"] = $"Ошибка анализа: {ex.Message}";
        }

        TempData["Deleted"] = dataFromCsv.deleted;
        TempData["Inserted"] = dataFromCsv.inserted;
        TempData["Updated"] = dataFromCsv.updated;
        TempData["SnapshotRows"] = dataFromCsv.snapshotRows;
        TempData["DateFolder"] = model.DateFolder;
        return RedirectToAction(nameof(Index));
    }

    /// <summary>
    /// Для перехода на Политику Конфедециальности
    /// </summary>
    /// <returns></returns>
    public IActionResult Privacy() => View(); 

    /// <summary>
    /// Полная очистка таблицы ApplicantsCurrent (испытание №2а)
    /// </summary>
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Clear(CancellationToken ct)
    {
        await _import.ClearAsync(ct);
        TempData["Cleared"] = true;
        TempData["Deleted"] = 0;
        TempData["Inserted"] = 0;
        TempData["Updated"] = 0;
        TempData["SnapshotRows"] = 0;
        return RedirectToAction(nameof(Index));
    }
}
