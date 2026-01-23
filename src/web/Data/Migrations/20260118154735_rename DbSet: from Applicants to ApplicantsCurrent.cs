using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace WebApp.Migrations
{
    /// <inheritdoc />
    public partial class renameDbSetfromApplicantstoApplicantsCurrent : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Applicants");

            migrationBuilder.CreateTable(
                name: "ApplicantsCurrent",
                columns: table => new
                {
                    ApplicantId = table.Column<int>(type: "INTEGER", nullable: false),
                    Program = table.Column<int>(type: "INTEGER", nullable: false),
                    Consent = table.Column<bool>(type: "INTEGER", nullable: false),
                    Priority = table.Column<int>(type: "INTEGER", nullable: false),
                    PhysicsIct = table.Column<int>(type: "INTEGER", nullable: false),
                    Russian = table.Column<int>(type: "INTEGER", nullable: false),
                    Math = table.Column<int>(type: "INTEGER", nullable: false),
                    Individual = table.Column<int>(type: "INTEGER", nullable: false),
                    Total = table.Column<int>(type: "INTEGER", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ApplicantsCurrent", x => new { x.Program, x.ApplicantId });
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ApplicantsCurrent");

            migrationBuilder.CreateTable(
                name: "Applicants",
                columns: table => new
                {
                    Program = table.Column<int>(type: "INTEGER", nullable: false),
                    ApplicantId = table.Column<int>(type: "INTEGER", nullable: false),
                    Consent = table.Column<bool>(type: "INTEGER", nullable: false),
                    Individual = table.Column<int>(type: "INTEGER", nullable: false),
                    Math = table.Column<int>(type: "INTEGER", nullable: false),
                    PhysicsIct = table.Column<int>(type: "INTEGER", nullable: false),
                    Priority = table.Column<int>(type: "INTEGER", nullable: false),
                    Russian = table.Column<int>(type: "INTEGER", nullable: false),
                    Total = table.Column<int>(type: "INTEGER", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Applicants", x => new { x.Program, x.ApplicantId });
                });
        }
    }
}
