namespace WebApp.Data.Entities;
public enum ProgramCode { PM, IVT, ITSS, IB }

/// <summary>
/// Модель для БД(таблица ApplicantsCurrent)
/// </summary>
public class ApplicantsCurrent
{
    public int ApplicantId { get; set; } // ID из csv-файлов
    public ProgramCode Program { get; set; } // ПМ, ИБ, ИТСС, ИВТ
    public bool Consent { get; set; } // согласие о зачислении
    public int Priority { get; set; } // приоритет абитуриента на данную программу
    public int PhysicsIct { get; set; } // баллы физика/икт
    public int Russian { get; set; } // баллы русский язык
    public int Math { get; set; } // баллы математика
    public int Individual { get; set; } // баллы индивидуальные достижения
    public int Total { get; set; } // сумма баллов 
}
