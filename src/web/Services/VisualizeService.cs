using System;
using Microsoft.EntityFrameworkCore;
using WebApp.Data.Entities;
using WebApp.Models.DTO;
using WebApp.Repositories;

namespace WebApp.Services;

public class VisualizeService
{
    private readonly IApplicantsCurrentRepository _repo;
    public VisualizeService(IApplicantsCurrentRepository repo) => _repo = repo;

    /// <summary>
    /// Возвращает отфильтрованный и отсортированный список абитуриентов + общее количество (для пагинации).
    /// </summary>
    public async Task<(int totalCount, List<VisualizeItemDto> items)> GetDataByQueryAsync(
        VisualizeQueryDto visualizeQuery,
        CancellationToken ct)
    {
        var page = Math.Max(1, visualizeQuery.Page ?? 1);
        var pageSize = Math.Clamp(visualizeQuery.PageSize ?? 100, 1, 500);

        var applicants = _repo.AsNoTracking(ct); // быстрота работы

        if (visualizeQuery.Program != null) applicants = applicants.Where(x => x.Program == visualizeQuery.Program);
        if (visualizeQuery.Consent != null) applicants = applicants.Where(x => x.Consent == visualizeQuery.Consent);
        if (visualizeQuery.Priority != null) applicants = applicants.Where(x => x.Priority == visualizeQuery.Priority);
        if (visualizeQuery.MinTotal != null) applicants = applicants.Where(x => x.Total >= visualizeQuery.MinTotal);
        if (visualizeQuery.MaxTotal != null) applicants = applicants.Where(x => x.Total <= visualizeQuery.MaxTotal);

        // базовый поиск по ApplicantId(позже мб будет больше Search'ей)
        if (!string.IsNullOrWhiteSpace(visualizeQuery.Search))
        {
            var search = visualizeQuery.Search.Trim();
            if (int.TryParse(search, out var id))
                applicants = applicants.Where(x => x.ApplicantId == id);
            else
                applicants = applicants.Where(x => x.ApplicantId.ToString().Contains(search));
        }

        applicants = ApplySort(applicants, visualizeQuery.SortBy, visualizeQuery.Desc ?? true);

        var totalCount = await applicants.CountAsync(ct);

        // ПАГИНАЦИЯ(разделение огромного количества информации на маленькие равные кусочки)
        // Select нужен, чтобы не смешивать front и БД ef'ы
        var items = await applicants
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(x => new VisualizeItemDto
            {
                ApplicantId = x.ApplicantId,
                Program = x.Program,
                Consent = x.Consent,
                Priority = x.Priority,
                PhysicsIct = x.PhysicsIct,
                Russian = x.Russian,
                Math = x.Math,
                Individual = x.Individual,
                Total = x.Total
            })
            .ToListAsync(ct);

        return (totalCount, items);
    }

    /// <summary>
    /// Внутренний метод для применения сортировки по чему-либо(enum лень было добавлять :) )
    /// </summary>
    /// <param name="applicants"></param>
    /// <param name="sortBy"></param>
    /// <param name="desc"></param>
    /// <returns></returns>
    private IQueryable<ApplicantsCurrent> ApplySort(IQueryable<ApplicantsCurrent> applicants, string sortBy, bool desc)
    {
        var key = (sortBy ?? string.Empty).Trim().ToLowerInvariant();

        // фильтрация по разным признакам
        applicants = key switch
        {
            "priority" => desc ? applicants.OrderByDescending(x => x.Priority) : applicants.OrderBy(x => x.Priority),
            "applicantid" => desc ? applicants.OrderByDescending(x => x.ApplicantId) : applicants.OrderBy(x => x.ApplicantId),
            "program" => desc ? applicants.OrderByDescending(x => x.Program) : applicants.OrderBy(x => x.Program),
            _ => desc ? applicants.OrderByDescending(x => x.Total) : applicants.OrderBy(x => x.Total) // default сортировка(по "Total")
        };

        return applicants;
    }
}
