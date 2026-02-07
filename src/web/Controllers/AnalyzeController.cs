using Microsoft.AspNetCore.Mvc;
using WebApp.Services;

namespace WebApp.Controllers
{
    public class AnalyzeController : Controller
    {
        private readonly AnalysisService _analysisService;

        public AnalyzeController(AnalysisService analysisService)
        {
            _analysisService = analysisService;
        }

        /// <summary>
        /// Анализ данных за конкретный день, например "01" или "02".
        /// </summary>
        /// <param name="day">Имя папки дня (01-04)</param>
        [HttpGet]
        public async Task<IActionResult> AnalyzeDay(string day)
        {
            if (string.IsNullOrWhiteSpace(day))
                return BadRequest("Нужно передать параметр day, например ?day=01");

            var result = await _analysisService.AnalyzeAsync(day);
            return Json(result);
        }

        /// <summary>
        /// Параллельный анализ всех дней (01-04) с возвратом JSON.
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> AnalyzeAll()
        {
            var results = await _analysisService.AnalyzeAllDaysAsync();
            return Json(results);
        }

        /// <summary>
        /// Параллельный анализ всех дней (01-04) с возвратом JSON.
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> GetPdf()
        {
            var res = await _analysisService.GeneratePdfReportAsync("01,02,03,04", "04");
            return View();
        }
    }
}
