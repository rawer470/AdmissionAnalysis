using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using WebApp.Data;
using WebApp.Data.Entities;

namespace WebApp.Repositories;

/// <summary>
/// Класс-репозиторий для доп прослойки между БД и бизнес-логикой, отвечает за ≈CRUD
/// </summary>
public sealed class ApplicantsCurrentRepository : IApplicantsCurrentRepository
{
    private readonly AdmissionContext _db;
    public ApplicantsCurrentRepository(AdmissionContext db) => _db = db;

    public Task<List<ApplicantsCurrent>> GetAllAsync(CancellationToken ct) =>
        _db.ApplicantsCurrent.ToListAsync(ct);

    public Task AddRangeAsync(IEnumerable<ApplicantsCurrent> items, CancellationToken ct)
    {
        _db.ApplicantsCurrent.AddRange(items);
        return Task.CompletedTask;
    }

    public void RemoveRange(IEnumerable<ApplicantsCurrent> items) =>
        _db.ApplicantsCurrent.RemoveRange(items);

    public async Task<int> SaveChangesAsync(CancellationToken ct) =>
        await _db.SaveChangesAsync(ct);


    public async Task<IDbContextTransaction> BeginTransactionAsync(CancellationToken ct) =>
        await _db.Database.BeginTransactionAsync(ct);
}
