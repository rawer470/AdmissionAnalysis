using Microsoft.EntityFrameworkCore;
using WebApp.Data;
using WebApp.Repositories;
using WebApp.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();

// Регистрация сервиса для добавления БД
builder.Services.AddDbContext<AdmissionContext>(options =>
    options.UseSqlite(builder.Configuration.
    GetConnectionString("MyDataBase")));

builder.Services.AddScoped<IApplicantsCurrentRepository, ApplicantsCurrentRepository>();
builder.Services.AddScoped<ImportService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseRouting();

app.UseAuthorization();

app.MapStaticAssets();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Admission}/{action=Index}/{id?}")
    .WithStaticAssets();


app.Run();
