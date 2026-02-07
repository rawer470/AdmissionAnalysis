using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace WebApp.Controllers
{
    /// <summary>
    /// Контроллер для отображения статистики зачисления
    /// </summary>
    public class StatisticsController : Controller
    {
        private readonly string _reportsPath;
        private readonly string[] _days = { "01", "02", "03", "04" };

        public StatisticsController(IWebHostEnvironment env)
        {
            // Путь к папке data/reports относительно корня проекта
            _reportsPath = Path.Combine(env.ContentRootPath, "..", "..", "data", "reports");
        }

        /// <summary>
        /// Главная страница статистики
        /// </summary>
        public ActionResult Index()
        {
            // Проверяем наличие данных
            var availableDays = _days.Where(d =>
                System.IO.File.Exists(Path.Combine(_reportsPath, d, "stats.json"))).ToList();

            ViewBag.AvailableDays = availableDays;

            // Динамически находим PDF и PNG файлы
            var (pdfPath, pngPath) = FindLatestReport();
            ViewBag.HasPdf = pdfPath != null;
            ViewBag.HasChart = pngPath != null;

            return View();
        }

        /// <summary>
        /// Находит последний сгенерированный отчет (PDF и PNG)
        /// </summary>
        private (string? pdfPath, string? pngPath) FindLatestReport()
        {
            if (!Directory.Exists(_reportsPath))
                return (null, null);

            // Ищем все PDF файлы с паттерном report_*.pdf
            var pdfFiles = Directory.GetFiles(_reportsPath, "report_*.pdf")
                .OrderByDescending(f => new FileInfo(f).LastWriteTime)
                .FirstOrDefault();

            string? pngPath = null;
            if (pdfFiles != null)
            {
                // Ищем соответствующий PNG
                pngPath = Path.ChangeExtension(pdfFiles, ".png");
                if (!System.IO.File.Exists(pngPath))
                    pngPath = null;
            }

            return (pdfFiles, pngPath);
        }

        /// <summary>
        /// Скачивание PDF отчета
        /// </summary>
        [HttpGet]
        public IActionResult DownloadPdf()
        {
            var (pdfPath, _) = FindLatestReport();

            if (pdfPath == null || !System.IO.File.Exists(pdfPath))
            {
                return NotFound("PDF отчет не найден. Сначала загрузите данные.");
            }

            var fileBytes = System.IO.File.ReadAllBytes(pdfPath);
            var fileName = Path.GetFileName(pdfPath);
            return File(fileBytes, "application/pdf", fileName);
        }

        /// <summary>
        /// Получение PNG графика динамики
        /// </summary>
        [HttpGet]
        public IActionResult GetChartImage()
        {
            var (_, pngPath) = FindLatestReport();

            if (pngPath == null || !System.IO.File.Exists(pngPath))
            {
                return NotFound("График не найден.");
            }

            var fileBytes = System.IO.File.ReadAllBytes(pngPath);
            return File(fileBytes, "image/png");
        }

        /// <summary>
        /// Получение статистики за конкретный день (JSON)
        /// </summary>
        [HttpGet]
        public IActionResult GetDayStats(string day)
        {
            if (string.IsNullOrEmpty(day) || !_days.Contains(day))
            {
                return BadRequest("Некорректный день. Допустимые значения: 01, 02, 03, 04");
            }

            var statsPath = Path.Combine(_reportsPath, day, "stats.json");

            if (!System.IO.File.Exists(statsPath))
            {
                return NotFound($"Статистика за день {day} не найдена.");
            }

            var json = System.IO.File.ReadAllText(statsPath);
            return Content(json, "application/json");
        }

        /// <summary>
        /// Получение статистики за все дни (JSON)
        /// </summary>
        [HttpGet]
        public IActionResult GetAllStats()
        {
            var result = new Dictionary<string, object>();

            foreach (var day in _days)
            {
                var statsPath = Path.Combine(_reportsPath, day, "stats.json");

                if (System.IO.File.Exists(statsPath))
                {
                    var json = System.IO.File.ReadAllText(statsPath);
                    var data = JsonSerializer.Deserialize<JsonElement>(json);
                    result[day] = data;
                }
            }

            return Json(result);
        }

        /// <summary>
        /// Получение динамики проходных баллов (JSON для графика)
        /// </summary>
        [HttpGet]
        public IActionResult GetPassingScoreDynamics()
        {
            var dynamics = new Dictionary<string, List<int?>>();
            var days = new List<string>();
            var programs = new[] { "pm", "ivt", "itss", "ib" };

            foreach (var prog in programs)
            {
                dynamics[prog] = new List<int?>();
            }

            foreach (var day in _days)
            {
                var statsPath = Path.Combine(_reportsPath, day, "stats.json");

                if (System.IO.File.Exists(statsPath))
                {
                    days.Add(day);
                    var json = System.IO.File.ReadAllText(statsPath);
                    var data = JsonSerializer.Deserialize<JsonElement>(json);

                    if (data.TryGetProperty("passing_score", out var passingScore))
                    {
                        foreach (var prog in programs)
                        {
                            if (passingScore.TryGetProperty(prog, out var score))
                            {
                                dynamics[prog].Add(score.ValueKind == JsonValueKind.Null ? null : score.GetInt32());
                            }
                            else
                            {
                                dynamics[prog].Add(null);
                            }
                        }
                    }
                }
            }

            return Json(new { days, dynamics });
        }

        /// <summary>
        /// Получение списка доступных дней
        /// </summary>
        [HttpGet]
        public IActionResult GetAvailableDays()
        {
            var availableDays = _days.Where(d =>
                System.IO.File.Exists(Path.Combine(_reportsPath, d, "stats.json"))).ToList();

            return Json(availableDays);
        }
    }
}
