using System;
using WebApp.Data.Entities;

namespace WebApp.Models.DTO;

/// <summary>
/// DTO. Нужна, когда фронтенд отправляет в бекенд запрос на изменение визуализации
/// </summary>
public sealed class VisualizeQueryDto
{
    public ProgramCode? Program { get; set; }      // null => вся БД
    public bool? Consent { get; set; }             // null => все
    public int? Priority { get; set; }             // null => все
    public int? MinTotal { get; set; }             // фильтр
    public int? MaxTotal { get; set; }

    public string? Search { get; set; }            // например по ApplicantId (строкой)
    
    public string SortBy { get; set; } = "Total";  // Total / Priority / ApplicantId
    public bool? Desc { get; set; } = true;          // Descending(По убыванию/возрастанию)

    public int? Page { get; set; } = 1;             // 1..N
    public int? PageSize { get; set; } = 100;       // 50/100/200
}
