using System;
using WebApp.Data.Entities;
using WebApp.Repositories;

namespace WebApp.Services;

public class ImportService
{
    private readonly IApplicantsCurrentRepository _repo;
    public ImportService(IApplicantsCurrentRepository repo) => _repo = repo;
    private static (ProgramCode p, int id) Key(ProgramCode p, int id) => (p, id); // для упрощения

    /// <summary>
    /// Метод-помощник для склеивания текущего дня(List<ApplicantsCurrent>) с предыдущими и записью этого в БД
    /// </summary>
    /// <param name="snapshotRows"></param>
    /// <param name="ct"></param>
    /// <returns></returns>
    /// <exception cref="InvalidOperationException"></exception>
    public async Task<(int deleted, int inserted, int updated)> ApplySnapshotAsync(
        IReadOnlyList<ApplicantsCurrent> snapshotRows,
        CancellationToken ct)
    {
        // 1) проверка уникальности ключа внутри snapshot(данных текущего дня)
        var snapKeys = new HashSet<(ProgramCode, int)>(snapshotRows.Count);
        foreach (var r in snapshotRows)
            if (!snapKeys.Add(Key(r.Program, r.ApplicantId)))
                throw new InvalidOperationException($"Duplicate key in snapshot: {r.Program}/{r.ApplicantId}");

        // Открытие транзакции
        await using var tx = await _repo.BeginTransactionAsync(ct);

        // 2) Считывание current одним запросом(текущее состояние)
        var currentAll = await _repo.GetAllAsync(ct);
        var curMap = currentAll.ToDictionary(x => Key(x.Program, x.ApplicantId));

        // 3) DELETE: есть в current, нет в snapshot(данных текущего дня)
        var toDelete = currentAll
            .Where(c => !snapKeys.Contains(Key(c.Program, c.ApplicantId)))
            .ToList();

        // 4) INSERT/UPDATE по snapshot(данным текущего дня)
        int deleted = toDelete.Count, inserted = 0, updated = 0;

        if (deleted > 0)
            _repo.RemoveRange(toDelete);

        var toInsert = new List<ApplicantsCurrent>();
        foreach (var s in snapshotRows)
        {
            var k = Key(s.Program, s.ApplicantId);

            if (!curMap.TryGetValue(k, out var cur))
            {
                toInsert.Add(s);
                inserted++;
                continue;
            }

            // update только если хоть что-то изменилось
            if (cur.Consent != s.Consent ||
                cur.Priority != s.Priority ||
                cur.PhysicsIct != s.PhysicsIct ||
                cur.Russian != s.Russian ||
                cur.Math != s.Math ||
                cur.Individual != s.Individual ||
                cur.Total != s.Total)
            {
                cur.Consent = s.Consent;
                cur.Priority = s.Priority;
                cur.PhysicsIct = s.PhysicsIct;
                cur.Russian = s.Russian;
                cur.Math = s.Math;
                cur.Individual = s.Individual;
                cur.Total = s.Total;
                updated++;
            }
        }

        if (toInsert.Count > 0)
            await _repo.AddRangeAsync(toInsert, ct);

        await _repo.SaveChangesAsync(ct);

        // Закрытие транзакции(коммит всех изменений) см. метод BeginTransactionAsync для более подроюной информации
        await tx.CommitAsync(ct);

        System.Console.WriteLine($"DELETED: {deleted}, INSERTED: {inserted}, UPDATED: {updated}");

        return (deleted, inserted, updated);
    }

    /// <summary>
    /// Метод для склеивания текущего дня(csv) с предыдущими и записью этого в БД
    /// </summary>
    /// <param name="pm">csv для ПМ</param>
    /// <param name="ivt">csv для ИВТ</param>
    /// <param name="itss">csv для ИТСС</param>
    /// <param name="ib">csv для ИБ</param>
    /// <param name="ct"></param>
    /// <returns></returns>
    public async Task<(int deleted, int inserted, int updated, int snapshotRows)> ImportDayAsync(
    IFormFile pm, IFormFile ivt, IFormFile itss, IFormFile ib,
    CancellationToken ct)
    {
        var snap = new List<ApplicantsCurrent>(140_000);

        using (var s = pm.OpenReadStream()) snap.AddRange(ApplicantsCsvParser.ParseCsv(s, ProgramCode.PM));
        using (var s = ivt.OpenReadStream()) snap.AddRange(ApplicantsCsvParser.ParseCsv(s, ProgramCode.IVT));
        using (var s = itss.OpenReadStream()) snap.AddRange(ApplicantsCsvParser.ParseCsv(s, ProgramCode.ITSS));
        using (var s = ib.OpenReadStream()) snap.AddRange(ApplicantsCsvParser.ParseCsv(s, ProgramCode.IB));

        var (deleted, inserted, updated) = await ApplySnapshotAsync(snap, ct);
        return (deleted, inserted, updated, snap.Count);
    }

}
