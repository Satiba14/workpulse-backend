const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  ImageRun,
  AlignmentType,
  BorderStyle,
  WidthType,
  ShadingType,
  VerticalAlign,
  HeadingLevel,
} = require("docx");
const fs = require("fs");
const path = require("path");

// ── Border helper ──────────────────────────────────────────────────────────
const border = { style: BorderStyle.SINGLE, size: 1, color: "2563EB" };
const borders = { top: border, bottom: border, left: border, right: border };

// ── Cell helpers ───────────────────────────────────────────────────────────
const labelCell = (text) =>
  new TableCell({
    width: { size: 4200, type: WidthType.DXA },
    borders,
    shading: { fill: "EFF6FF", type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 150, right: 150 },
    children: [
      new Paragraph({
        children: [
          new TextRun({ text, bold: true, size: 20, font: "Arial", color: "1E40AF" }),
        ],
      }),
    ],
  });

const valueCell = (text) =>
  new TableCell({
    width: { size: 5160, type: WidthType.DXA },
    borders,
    margins: { top: 100, bottom: 100, left: 150, right: 150 },
    children: [
      new Paragraph({
        children: [
          new TextRun({ text: text || "—", size: 20, font: "Arial", color: "1F2937" }),
        ],
      }),
    ],
  });

const row = (label, value) =>
  new TableRow({ children: [labelCell(label), valueCell(value)] });

// ── Section heading row ────────────────────────────────────────────────────
const sectionRow = (title) =>
  new TableRow({
    children: [
      new TableCell({
        columnSpan: 2,
        width: { size: 9360, type: WidthType.DXA },
        borders,
        shading: { fill: "1D4ED8", type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: title, bold: true, size: 20, font: "Arial", color: "FFFFFF" }),
            ],
          }),
        ],
      }),
    ],
  });

// ── Main generator function ────────────────────────────────────────────────
async function generateEmployeeLetter(data) {
  const {
    first_name, last_name, emp_id,
    department, reporting_to, joined_on,
    designation, email, official_email,
    monthly_pay_0_6, monthly_pay_6_12,
    pay_label_0_6, pay_label_6_12,
    is_fresher,
    revision_period, next_revision_date,
    bond, photo_base64, photo_type,
    custom_fields,
  } = data;

  // ── Header section — logo strictly left-aligned, modest size ───────────
  const logoPath = path.join(__dirname, "assets", "invenger-logo.png");
  let headerChildren = [];

  if (fs.existsSync(logoPath)) {
    const logoBuffer = fs.readFileSync(logoPath);
    headerChildren.push(
      new Paragraph({
        alignment: AlignmentType.LEFT,
        indent: { left: 0 },
        spacing: { after: 120 },
        children: [
          new ImageRun({
            data: logoBuffer,
            type: "png",
            transformation: { width: 90, height: 29 },
          }),
        ],
      })
    );
  } else {
    headerChildren.push(
      new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { after: 80 },
        children: [
          new TextRun({ text: "INVENGER TECHNOLOGIES", bold: true, size: 32, font: "Arial", color: "1D4ED8" }),
        ],
      })
    );
  }

  const headerParagraphs = [
    ...headerChildren,
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: [
        new TextRun({ text: "Employee Details Document", size: 24, font: "Arial", color: "6B7280" }),
      ],
    }),
    new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2563EB", space: 1 } },
      spacing: { after: 300 },
      children: [],
    }),
  ];

  // ── Photo row (if provided) ────────────────────────────────────────────
  let photoRows = [];
  if (photo_base64) {
    try {
      const photoBuffer = Buffer.from(photo_base64, "base64");
      const mediaType = (photo_type || "image/jpeg").includes("png") ? "png" : "jpeg";
      photoRows = [
        new TableRow({
          children: [
            labelCell("Photo"),
            new TableCell({
              width: { size: 5160, type: WidthType.DXA },
              borders,
              margins: { top: 100, bottom: 100, left: 150, right: 150 },
              children: [
                new Paragraph({
                  children: [
                    new ImageRun({
                      data: photoBuffer,
                      type: mediaType,
                      transformation: { width: 80, height: 100 },
                    }),
                  ],
                }),
              ],
            }),
          ],
        }),
      ];
    } catch (e) {
      console.error("Photo error:", e.message);
    }
  }

  // ── Main table ─────────────────────────────────────────────────────────
  const mainTable = new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [4200, 5160],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            columnSpan: 2,
            width: { size: 9360, type: WidthType.DXA },
            borders,
            shading: { fill: "1E3A8A", type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 150, right: 150 },
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "PARTICULARS  |  EMPLOYEE DETAILS", bold: true, size: 22, font: "Arial", color: "FFFFFF" }),
                ],
              }),
            ],
          }),
        ],
      }),

      sectionRow("Personal Information"),
      row("First Name", first_name || ""),
      row("Last Name", last_name || ""),
      row("Emp ID", emp_id || ""),
      ...photoRows,

      sectionRow("Professional Information"),
      row("Team / Department", department || ""),
      row("Reporting To", reporting_to || ""),
      row("Joining Date", joined_on || ""),
      row("Designation", designation || ""),

      sectionRow("Contact Information"),
      row("Email Address", email || ""),
      row("Official Email Address", official_email || ""),

      sectionRow("Compensation & Benefits"),
      row(pay_label_0_6 || "Monthly Pay", monthly_pay_0_6 || ""),
      ...(is_fresher
        ? [row(pay_label_6_12 || "Monthly Pay Apprentice", monthly_pay_6_12 || "")]
        : []),
      row("Revision Period", revision_period || ""),
      row("Next Revision Date", next_revision_date || ""),
      row("Bond", bond || ""),
      ...(Array.isArray(custom_fields) && custom_fields.length > 0
        ? [
            sectionRow("Additional Information"),
            ...custom_fields
              .filter((f) => f && f.label && f.label.trim() !== "")
              .map((f) => row(f.label, f.value || "")),
          ]
        : []),
    ],
  });

  // ── Footer ─────────────────────────────────────────────────────────────
  const footer = [
    new Paragraph({
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: "2563EB", space: 1 } },
      spacing: { before: 300, after: 80 },
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: "Invenger Technologies — Confidential Document", size: 16, font: "Arial", color: "9CA3AF" }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: `Generated on ${new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "long", year: "numeric" })}`,
          size: 16, font: "Arial", color: "9CA3AF",
        }),
      ],
    }),
  ];

  // ── Build document ─────────────────────────────────────────────────────
  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            size: { width: 12240, height: 15840 },
            margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
          },
        },
        children: [...headerParagraphs, mainTable, ...footer],
      },
    ],
  });

  return await Packer.toBuffer(doc);
}

module.exports = { generateEmployeeLetter };