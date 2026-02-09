using System;
using Microsoft.EntityFrameworkCore;
using WebApp.Data.Entities;

namespace WebApp.Data;
/// <summary>
/// DbContext для БД ApplicantsCurrent.db
/// </summary>
public class AdmissionContext : DbContext
{
    public AdmissionContext(DbContextOptions<AdmissionContext> options) : base(options) { } // Конструктор для поднятия БД
    public DbSet<ApplicantsCurrent> ApplicantsCurrent { get; set; } // Список ApplicantsCurrent для дальнейшего обращения к нему с помощью EF Core

    protected override void OnModelCreating(ModelBuilder mb)
    {
        // Первичный ключ для ApplicantsCurrent: (ProgramCode program, int id)
        mb.Entity<ApplicantsCurrent>().HasKey(x => new { x.Program, x.ApplicantId }); 

        base.OnModelCreating(mb); // на всякий случай даем базовому классу отработать
    }
}
