using Microsoft.EntityFrameworkCore.Storage;
using WebApp.Data.Entities;

namespace WebApp.Repositories;

public interface IApplicantsCurrentRepository
{
    /// <summary>
    /// получить текущее состояние таблицы ApplicantsCurrent целиком
    /// </summary>
    /// <param name="ct">Нужен для корректной остановки работы, если она прервется</param>
    /// <returns></returns>
    Task<List<ApplicantsCurrent>> GetAllAsync(CancellationToken ct); // получить все 
    /// <summary>
    /// добавить много ApplicantsCurrent
    /// </summary>
    /// <param name="items"></param>
    /// <param name="ct">Нужен для корректной остановки работы, если она прервется</param>
    /// <returns></returns>
    Task AddRangeAsync(IEnumerable<ApplicantsCurrent> items, CancellationToken ct);

    /// <summary>
    /// удалить много ApplicantsCurrent
    /// </summary>
    /// <param name="items"></param>
    void RemoveRange(IEnumerable<ApplicantsCurrent> items);

    /// <summary>
    /// сохранить данные
    /// </summary>
    /// <param name="ct">Нужен для корректной остановки работы, если она прервется</param>
    /// <returns></returns>
    Task<int> SaveChangesAsync(CancellationToken ct);

    /// <summary>
    /// начало транзакции. Делает все изменения после него атомарными. Без него - каждый SaveChangesAsync() — своя собственная транзакция.
    /// ------------------------------
    /// P. S. атомарность — это свойство операции, при котором она выполняется целиком или не выполняется вовсе.
    /// </summary>
    /// <param name="ct">Нужен для корректной остановки работы, если она прервется</param>
    /// <returns></returns>
    Task<IDbContextTransaction> BeginTransactionAsync(CancellationToken ct);

    /// <summary>
    /// Нужен для получения списка кого-то без его отслеживания(без возможности изменения объектов). Работает быстрее GetAllAsync
    /// </summary>
    /// <param name="ct"></param>
    /// <returns></returns>
    public IQueryable<ApplicantsCurrent> AsNoTracking(CancellationToken ct);
}
