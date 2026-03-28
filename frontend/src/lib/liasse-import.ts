const LIASSE_FIELD_LABELS = {
  siren: "SIREN",
  exercice_clos: "Exercice clos le",
  benefice_comptable: "Benefice comptable",
  perte_comptable: "Perte comptable",
  wi_is_comptabilise: "WI - IS comptabilise",
  wg_amendes_penalites: "WG - Amendes et penalites",
  wm_interets_excedentaires: "WM - Interets excedentaires",
  wn_reintegrations_diverses: "WN - Reintegrations diverses",
  wv_regime_mere_filiale: "WV - Deduction mere-filiale",
  l8_qp_12pct: "L8 - QP frais 12%",
  ca: "CA HT",
  capital_pp: "Capital >= 75% personnes physiques",
  save: "Sauvegarder le calcul",
} as const;

const FIELD_ALIASES = {
  siren: ["siren"],
  exercice_clos: [
    "exercice_clos",
    "exercice clos le",
    "exercice clos",
    "exercice",
    "date cloture",
    "date de cloture",
    "cloture",
  ],
  benefice_comptable: [
    "benefice_comptable",
    "benefice comptable",
    "benefice",
    "xn",
    "ligne xn",
  ],
  perte_comptable: [
    "perte_comptable",
    "perte comptable",
    "perte",
  ],
  wi_is_comptabilise: [
    "wi_is_comptabilise",
    "wi",
    "wi is comptabilise",
    "is comptabilise",
  ],
  wg_amendes_penalites: [
    "wg_amendes_penalites",
    "wg",
    "wg amendes penalites",
    "amendes penalites",
    "amendes",
    "penalites",
  ],
  wm_interets_excedentaires: [
    "wm_interets_excedentaires",
    "wm",
    "wm interets excedentaires",
    "interets excedentaires",
    "interets",
  ],
  wn_reintegrations_diverses: [
    "wn_reintegrations_diverses",
    "wn",
    "wn reintegrations diverses",
    "reintegrations diverses",
    "reintegrations",
  ],
  wv_regime_mere_filiale: [
    "wv_regime_mere_filiale",
    "wv",
    "wv regime mere filiale",
    "regime mere filiale",
    "mere filiale",
  ],
  l8_qp_12pct: [
    "l8_qp_12pct",
    "l8",
    "l8 qp 12 pct",
    "qp 12 pct",
    "quote part 12",
  ],
  ca: [
    "ca",
    "ca ht",
    "chiffre affaires",
    "chiffre affaires ht",
    "chiffre d affaires",
    "chiffre d affaires ht",
  ],
  capital_pp: [
    "capital_pp",
    "capital pp",
    "capital 75",
    "capital personnes physiques",
    "capital detenu 75",
    "capital detenu 75 personnes physiques",
    "capital detenu personnes physiques",
  ],
  save: [
    "save",
    "save calculation",
    "sauvegarde",
    "sauvegarder",
    "enregistrer",
  ],
} as const;

const EXCEL_EXTENSIONS = [".xlsx", ".xls", ".xlsm", ".xlsb"];
const PDF_EXTENSIONS = [".pdf"];

const ALIAS_TO_FIELD = new Map<string, keyof typeof LIASSE_FIELD_LABELS>();
const LOOSE_TEXT_PATTERNS: Array<{
  field: keyof typeof LIASSE_FIELD_LABELS;
  aliasLength: number;
  regex: RegExp;
}> = [];

Object.entries(FIELD_ALIASES).forEach(([field, aliases]) => {
  aliases.forEach((alias) => {
    ALIAS_TO_FIELD.set(normalizeKey(alias), field as keyof typeof LIASSE_FIELD_LABELS);
    LOOSE_TEXT_PATTERNS.push({
      field: field as keyof typeof LIASSE_FIELD_LABELS,
      aliasLength: normalizeKey(alias).length,
      regex: buildLooseAliasPattern(alias),
    });
  });
});

LOOSE_TEXT_PATTERNS.sort((a, b) => b.aliasLength - a.aliasLength);

const NESTED_CONTAINERS = new Set([
  "liasse",
  "input",
  "inputdata",
  "payload",
  "values",
  "data",
]);

export type ImportableFieldKey = keyof typeof LIASSE_FIELD_LABELS;
export type LiasseImportFormValues = Partial<
  Record<Exclude<ImportableFieldKey, "ca" | "capital_pp" | "save">, string>
>;

export interface ParsedLiasseImport {
  fileName: string;
  importedFormValues: LiasseImportFormValues;
  ca?: string;
  capitalPP?: boolean;
  save?: boolean;
  matchedFieldKeys: ImportableFieldKey[];
}

export function getImportFieldLabel(field: ImportableFieldKey) {
  return LIASSE_FIELD_LABELS[field];
}

export async function parseImportedLiasseFile(file: File): Promise<ParsedLiasseImport> {
  const imported = buildImportAccumulator();
  const lowerName = file.name.toLowerCase();

  if (hasAnyExtension(lowerName, EXCEL_EXTENSIONS)) {
    await parseSpreadsheetFile(file, imported);
  } else if (hasAnyExtension(lowerName, PDF_EXTENSIONS)) {
    await parsePdfFile(file, imported);
  } else {
    const text = await file.text();
    parseTextContent(text, imported);
  }

  const matchedFieldKeys = Array.from(imported.matched);
  if (matchedFieldKeys.length === 0) {
    throw new Error(
      "Aucun champ reconnu. Utilisez un fichier JSON, CSV, TXT, Excel ou PDF avec des valeurs comme SIREN, benefice comptable, WI, WG, WM, WN, WV, L8, CA ou capital_pp."
    );
  }

  return {
    fileName: file.name,
    importedFormValues: imported.form,
    ca: imported.ca,
    capitalPP: imported.capitalPP,
    save: imported.save,
    matchedFieldKeys,
  };
}

function buildImportAccumulator() {
  return {
    form: {} as LiasseImportFormValues,
    ca: undefined as string | undefined,
    capitalPP: undefined as boolean | undefined,
    save: undefined as boolean | undefined,
    matched: new Set<ImportableFieldKey>(),
  };
}

async function parseSpreadsheetFile(
  file: File,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  const XLSX = await import("xlsx");
  const workbook = XLSX.read(await file.arrayBuffer(), { type: "array", cellDates: false });

  workbook.SheetNames.forEach((sheetName) => {
    const sheet = workbook.Sheets[sheetName];
    if (!sheet) {
      return;
    }

    const rows = XLSX.utils.sheet_to_json<(string | number | boolean)[]>(sheet, {
      header: 1,
      raw: false,
      defval: "",
      blankrows: false,
    });

    parseRows(rows, imported);
  });
}

async function parsePdfFile(
  file: File,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  const pdfjs = await import("pdfjs-dist");
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
  ).toString();

  const loadingTask = pdfjs.getDocument({
    data: new Uint8Array(await file.arrayBuffer()),
  });

  try {
    const document = await loadingTask.promise;
    const lines: string[] = [];

    for (let pageNumber = 1; pageNumber <= document.numPages; pageNumber += 1) {
      const page = await document.getPage(pageNumber);
      const textContent = await page.getTextContent();
      lines.push(...extractPdfLines(textContent.items as Array<Record<string, unknown>>));
    }

    parseTextContent(lines.join("\n"), imported);
  } catch {
    throw new Error("Impossible de lire ce PDF. Verifiez qu'il contient du texte exploitable.");
  } finally {
    await loadingTask.destroy();
  }
}

function parseTextContent(
  text: string,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  const trimmed = text.trim();

  if (!trimmed) {
    throw new Error("Le fichier est vide.");
  }

  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    parseJsonContent(trimmed, imported);
  } else if (looksDelimited(trimmed)) {
    parseDelimitedContent(trimmed, imported);
  } else {
    parseKeyValueText(trimmed, imported);
  }

  parseLooseTextContent(trimmed, imported);
}

function parseJsonContent(
  text: string,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  let parsed: unknown;

  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error("Le fichier JSON n'est pas valide.");
  }

  const candidates = Array.isArray(parsed) ? parsed : [parsed];
  const firstObject = candidates.find(isPlainObject);

  if (!firstObject) {
    throw new Error("Le JSON doit contenir un objet avec les champs de la liasse.");
  }

  collectFromObject(firstObject, imported);
}

function parseDelimitedContent(
  text: string,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  const delimiter = detectDelimiter(text);
  const rows = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => splitDelimitedLine(line, delimiter));

  parseRows(rows, imported);
}

function parseRows(
  rows: Array<Array<string | number | boolean>>,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  const normalizedRows = rows
    .map((row) => row.map((cell) => String(cell ?? "").trim()))
    .filter((row) => row.some((cell) => cell !== ""));

  if (normalizedRows.length === 0) {
    return;
  }

  if (normalizedRows.length >= 2 && shouldTreatAsHeaderTable(normalizedRows)) {
    const headers = normalizedRows[0];
    const firstDataRow = normalizedRows
      .slice(1)
      .find((row) => row.some((cell, index) => headers[index] && cell !== ""));

    if (!firstDataRow) {
      return;
    }

    headers.forEach((header, index) => {
      assignRecognizedValue(header, firstDataRow[index], imported);
    });
    return;
  }

  const startIndex =
    normalizedRows[0].length >= 2 &&
    isKeyLabel(normalizedRows[0][0]) &&
    isValueLabel(normalizedRows[0][1])
      ? 1
      : 0;

  normalizedRows.slice(startIndex).forEach((row) => {
    if (row.length >= 2) {
      assignRecognizedValue(row[0], row[1], imported);
    }
  });
}

function parseKeyValueText(
  text: string,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .forEach((line) => {
      const match = line.match(/^([^:=]+)\s*[:=]\s*(.+)$/);
      if (!match) {
        return;
      }

      assignRecognizedValue(match[1], match[2], imported);
    });
}

function parseLooseTextContent(
  text: string,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  text
    .split(/\r?\n/)
    .map((line) => simplifyLooseLine(line))
    .filter(Boolean)
    .forEach((line) => {
      for (const candidate of LOOSE_TEXT_PATTERNS) {
        const match = line.match(candidate.regex);
        if (!match) {
          continue;
        }

        assignImportedValue(candidate.field, match[1], imported);
        break;
      }
    });
}

function collectFromObject(
  source: Record<string, unknown>,
  imported: ReturnType<typeof buildImportAccumulator>,
  depth: number = 0
) {
  Object.entries(source).forEach(([rawKey, rawValue]) => {
    const field = resolveField(rawKey);
    if (field) {
      assignImportedValue(field, rawValue, imported);
      return;
    }

    if (depth < 2 && isPlainObject(rawValue) && NESTED_CONTAINERS.has(normalizeKey(rawKey))) {
      collectFromObject(rawValue, imported, depth + 1);
    }
  });
}

function assignRecognizedValue(
  rawKey: string,
  rawValue: unknown,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  const field = resolveField(rawKey);
  if (!field) {
    return;
  }

  assignImportedValue(field, rawValue, imported);
}

function assignImportedValue(
  field: ImportableFieldKey,
  rawValue: unknown,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  if (rawValue == null || rawValue === "") {
    return;
  }

  if (field === "capital_pp" || field === "save") {
    const parsedBoolean = parseBooleanValue(rawValue);
    if (parsedBoolean == null) {
      return;
    }

    if (field === "capital_pp") {
      imported.capitalPP = parsedBoolean;
    } else {
      imported.save = parsedBoolean;
    }
    imported.matched.add(field);
    return;
  }

  if (field === "ca") {
    const numericValue = normalizeNumericValue(rawValue);
    if (!numericValue) {
      return;
    }
    imported.ca = numericValue;
    imported.matched.add(field);
    return;
  }

  if (field === "siren") {
    const siren = String(rawValue).trim();
    if (!siren) {
      return;
    }
    imported.form[field] = siren;
    imported.matched.add(field);
    return;
  }

  if (field === "exercice_clos") {
    const dateValue = normalizeDateValue(rawValue);
    if (!dateValue) {
      return;
    }
    imported.form[field] = dateValue;
    imported.matched.add(field);
    return;
  }

  const numericValue = normalizeNumericValue(rawValue);
  if (!numericValue) {
    return;
  }

  imported.form[field] = numericValue;
  imported.matched.add(field);
}

function resolveField(rawKey: string) {
  return ALIAS_TO_FIELD.get(normalizeKey(rawKey));
}

function normalizeKey(value: string) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "");
}

function normalizeNumericValue(value: unknown) {
  if (typeof value === "number") {
    return Number.isFinite(value) ? String(value) : "";
  }

  const raw = String(value).trim();
  if (!raw) {
    return "";
  }

  const compact = raw
    .replace(/eur/gi, "")
    .replace(/\s+/g, "")
    .replace(/\u00a0/g, "");

  const commaCount = (compact.match(/,/g) || []).length;
  const dotCount = (compact.match(/\./g) || []).length;
  let normalized = compact;

  if (commaCount > 0 && dotCount > 0) {
    normalized =
      compact.lastIndexOf(",") > compact.lastIndexOf(".")
        ? compact.replace(/\./g, "").replace(",", ".")
        : compact.replace(/,/g, "");
  } else if (commaCount > 0) {
    const [, fractional = ""] = compact.split(",");
    normalized =
      fractional.length > 0 && fractional.length <= 2
        ? compact.replace(",", ".")
        : compact.replace(/,/g, "");
  }

  normalized = normalized.replace(/[^0-9.-]/g, "");
  return /^-?\d+(\.\d+)?$/.test(normalized) ? normalized : "";
}

function normalizeDateValue(value: unknown) {
  const raw = String(value).trim();
  if (!raw) {
    return "";
  }

  const isoMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (isoMatch) {
    return raw;
  }

  const frMatch = raw.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (frMatch) {
    const [, day, month, year] = frMatch;
    return `${year}-${month}-${day}`;
  }

  return raw;
}

function parseBooleanValue(value: unknown) {
  if (typeof value === "boolean") {
    return value;
  }

  if (typeof value === "number") {
    if (value === 1) return true;
    if (value === 0) return false;
  }

  const normalized = normalizeKey(String(value));
  if (["1", "true", "oui", "yes", "active", "on"].includes(normalized)) {
    return true;
  }
  if (["0", "false", "non", "no", "inactive", "off"].includes(normalized)) {
    return false;
  }

  return null;
}

function looksDelimited(text: string) {
  const firstLines = text.split(/\r?\n/).slice(0, 3).join("\n");
  return /[;,\t|]/.test(firstLines);
}

function detectDelimiter(text: string) {
  const sample = text.split(/\r?\n/).slice(0, 5).join("\n");
  const delimiters = [";", ",", "\t", "|"] as const;
  return delimiters.reduce(
    (best, delimiter) => {
      const score = (sample.match(new RegExp(`\\${delimiter}`, "g")) || []).length;
      return score > best.score ? { delimiter, score } : best;
    },
    { delimiter: ";" as (typeof delimiters)[number], score: -1 }
  ).delimiter;
}

function splitDelimitedLine(line: string, delimiter: string) {
  const values: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    const next = line[i + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === delimiter && !inQuotes) {
      values.push(current.trim());
      current = "";
      continue;
    }

    current += char;
  }

  values.push(current.trim());
  return values;
}

function shouldTreatAsHeaderTable(rows: string[][]) {
  const recognizedHeaders = rows[0].filter((cell) => resolveField(cell)).length;
  return recognizedHeaders >= 2 || (rows[0].length > 2 && recognizedHeaders >= 1);
}

function isKeyLabel(value: string) {
  return ["champ", "field", "key", "cle", "label"].includes(normalizeKey(value));
}

function isValueLabel(value: string) {
  return ["value", "valeur", "data", "donnee"].includes(normalizeKey(value));
}

function hasAnyExtension(fileName: string, extensions: string[]) {
  return extensions.some((extension) => fileName.endsWith(extension));
}

function buildLooseAliasPattern(alias: string) {
  const parts = alias
    .split(/[_\s-]+/)
    .filter(Boolean)
    .map((part) => escapeRegExp(part));

  return new RegExp(
    `^${parts.join("[\\\\s_\\-./()]*")}\\b\\s*[:=\\-]?\\s*(.+)$`,
    "i"
  );
}

function simplifyLooseLine(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\u00a0/g, " ")
    .replace(/[–—]/g, "-")
    .replace(/\s+/g, " ")
    .trim();
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function extractPdfLines(items: Array<Record<string, unknown>>) {
  const buckets = new Map<number, Array<{ x: number; text: string }>>();

  items.forEach((item) => {
    if (typeof item.str !== "string" || !item.str.trim()) {
      return;
    }

    const transform = Array.isArray(item.transform) ? item.transform : [];
    const x = typeof transform[4] === "number" ? transform[4] : 0;
    const y = typeof transform[5] === "number" ? transform[5] : 0;
    const bucketKey = Math.round(y / 4) * 4;
    const bucket = buckets.get(bucketKey) || [];
    bucket.push({ x, text: item.str.trim() });
    buckets.set(bucketKey, bucket);
  });

  return Array.from(buckets.entries())
    .sort((a, b) => b[0] - a[0])
    .map(([, entries]) =>
      entries
        .sort((a, b) => a.x - b.x)
        .map((entry) => entry.text)
        .join(" ")
        .replace(/\s+/g, " ")
        .trim()
    )
    .filter(Boolean);
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
