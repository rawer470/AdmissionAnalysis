using System.Text.Json;

namespace WebApp.Services;

/// <summary>
/// Сервис для вызова FastApi и проведения анализа таблиц и создания отчетов
/// </summary>
public class AnalysisService
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    public AnalysisService(HttpClient httpClient, string baseUrl = "http://localhost:8000")
    {
        _httpClient = httpClient;
        _baseUrl = baseUrl.TrimEnd('/');
    }

    /// <summary>
    /// Проверка здоровья API
    /// </summary>
    public async Task<JsonDocument> GetHealthAsync()
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/health");
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(content);
    }

    /// <summary>
    /// Получить список папок в uploads
    /// </summary>
    public async Task<JsonDocument> GetUploadsAsync()
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/api/uploads");
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(content);
    }

    /// <summary>
    /// Получить список программ
    /// </summary>
    public async Task<JsonDocument> GetProgramsAsync()
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/api/programs");
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(content);
    }

    /// <summary>
    /// Анализ CSV-файлов из папки с датой
    /// </summary>
    /// <param name="dateFolder">Имя папки (например: "01", "02", "03", "04")</param>
    /// <param name="capacityPm">Квота ПМ (по умолчанию 40)</param>
    /// <param name="capacityIvt">Квота ИВТ (по умолчанию 50)</param>
    /// <param name="capacityItss">Квота ИТСС (по умолчанию 30)</param>
    /// <param name="capacityIb">Квота ИБ (по умолчанию 20)</param>
    public async Task<JsonDocument> AnalyzeAsync(
        string dateFolder,
        int? capacityPm = null,
        int? capacityIvt = null,
        int? capacityItss = null,
        int? capacityIb = null)
    {
        var queryParams = new List<string>();
        if (capacityPm.HasValue) queryParams.Add($"capacity_pm={capacityPm}");
        if (capacityIvt.HasValue) queryParams.Add($"capacity_ivt={capacityIvt}");
        if (capacityItss.HasValue) queryParams.Add($"capacity_itss={capacityItss}");
        if (capacityIb.HasValue) queryParams.Add($"capacity_ib={capacityIb}");

        var url = $"{_baseUrl}/api/analyze/{dateFolder}";
        if (queryParams.Count > 0)
            url += "?" + string.Join("&", queryParams);

        var response = await _httpClient.GetAsync(url);
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(content);
    }

    /// <summary>
    /// Анализ CSV-файлов по всем дням (01, 02, 03, 04)
    /// </summary>
    /// <param name="dateFolders">Список папок для анализа (по умолчанию: 01, 02, 03, 04)</param>
    /// <param name="capacityPm">Квота ПМ (по умолчанию 40)</param>
    /// <param name="capacityIvt">Квота ИВТ (по умолчанию 50)</param>
    /// <param name="capacityItss">Квота ИТСС (по умолчанию 30)</param>
    /// <param name="capacityIb">Квота ИБ (по умолчанию 20)</param>
    /// <returns>Словарь: ключ - дата, значение - результат анализа</returns>
    public async Task<Dictionary<string, JsonDocument>> AnalyzeAllDaysAsync(
        string[]? dateFolders = null,
        int? capacityPm = null,
        int? capacityIvt = null,
        int? capacityItss = null,
        int? capacityIb = null)
    {
        dateFolders ??= ["01", "02", "03", "04"];

        var tasks = dateFolders.Select(async folder =>
        {
            var result = await AnalyzeAsync(folder, capacityPm, capacityIvt, capacityItss, capacityIb);
            return (folder, result);
        });

        var results = await Task.WhenAll(tasks);
        return results.ToDictionary(r => r.folder, r => r.result);
    }

    /// <summary>
    /// Генерация PDF-отчета из сохраненных stats.json
    /// </summary>
    /// <param name="dateFolders">Список папок через запятую (например: "01,02,03,04")</param>
    /// <param name="targetDate">Целевая дата для основного отчета</param>
    public async Task<JsonDocument> GeneratePdfReportAsync(
        string? dateFolders = null,
        string? targetDate = null)
    {
        var queryParams = new List<string>();
        if (!string.IsNullOrEmpty(dateFolders)) queryParams.Add($"date_folders={dateFolders}");
        if (!string.IsNullOrEmpty(targetDate)) queryParams.Add($"target_date={targetDate}");

        var url = $"{_baseUrl}/api/generate_pdf_report";
        if (queryParams.Count > 0)
            url += "?" + string.Join("&", queryParams);

        var response = await _httpClient.GetAsync(url);
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(content);
    }
}
