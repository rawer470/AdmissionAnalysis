using System;
using WebApp.Data.Entities;

namespace WebApp.Services;

/// <summary>
/// Класс-парсер для превращения csv-файлов в формат ApplicantsCurrent
/// </summary>
public class ApplicantsCsvParser
{
    /// <summary>
    /// Метод-парсер для превращения csv-файлов в формат ApplicantsCurrent
    /// </summary>
    /// <param name="stream"></param>
    /// <param name="program"></param>
    /// <returns></returns>
    /// <exception cref="InvalidOperationException"></exception>
    public static List<ApplicantsCurrent> ParseCsv(Stream stream, ProgramCode program)
    {
        using var sr = new StreamReader(stream, leaveOpen: true);

        string? headerLine = sr.ReadLine();
        if (headerLine is null) return new();

        char sep = headerLine.Contains(';') ? ';' : ',';
        var headers = headerLine.Split(sep).Select(x => x.Trim().ToLowerInvariant()).ToArray();

        int Col(string name)
        {
            int idx = Array.IndexOf(headers, name);
            if (idx < 0) throw new InvalidOperationException($"CSV missing column: {name}");
            return idx;
        }

        int cId = Col("id");
        int cConsent = Col("consent");
        int cPriority = Col("priority");
        int cPhys = Col("physics_ict");
        int cRus = Col("russian");
        int cMath = Col("math");
        int cInd = Col("individual");
        int cTotal = Col("total");

        var res = new List<ApplicantsCurrent>(8192);

        string? line;
        while ((line = sr.ReadLine()) != null)
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            var p = line.Split(sep);
            if (p.Length < headers.Length) continue;

            int id = int.Parse(p[cId].Trim());
            bool consent = p[cConsent].Trim() == "1";
            int priority = int.Parse(p[cPriority].Trim());

            int phys = int.Parse(p[cPhys].Trim());
            int rus = int.Parse(p[cRus].Trim());
            int math = int.Parse(p[cMath].Trim());
            int ind = int.Parse(p[cInd].Trim());
            int total = int.Parse(p[cTotal].Trim());

            res.Add(new ApplicantsCurrent
            {
                Program = program,
                ApplicantId = id,
                Consent = consent,
                Priority = priority,
                PhysicsIct = phys,
                Russian = rus,
                Math = math,
                Individual = ind,
                Total = total
            });
        }

        return res;
    }
}
