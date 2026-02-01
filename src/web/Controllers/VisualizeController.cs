using Microsoft.AspNetCore.Mvc;
using WebApp.Models.DTO;
using WebApp.Services;

namespace WebApp.Controllers
{
    public class VisualizeController : Controller
    {
        private readonly VisualizeService _service;

        public VisualizeController(VisualizeService service)
        {
            _service = service;
        }

        [HttpGet]
        public ActionResult Index()
        {
            return View();
        }

        [HttpGet]
        public async Task<IActionResult> GetData([FromQuery] VisualizeQueryDto visualizeQuery, CancellationToken ct)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var (totalCount, items) = await _service.GetDataByQueryAsync(visualizeQuery, ct);
            return Json(new { totalCount, items });
        }
    }
}
