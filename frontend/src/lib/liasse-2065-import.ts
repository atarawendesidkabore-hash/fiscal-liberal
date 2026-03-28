const LIASSE_2065_FIELD_LABELS = {
  siren: "SIREN",
  denomination: "Denomination",
  exercice_ouvert: "Exercice ouvert le",
  exercice_clos: "Exercice clos le",
  regime_imposition: "Regime d'imposition",
  ca_ht: "CA HT",
  capital_social: "Capital social",
  effectif_moyen: "Effectif moyen",
  capital_pp: "Capital >= 75% personnes physiques",
  capital_libere: "Capital entierement libere",
  resultat_comptable: "Resultat comptable",
  achats_marchandises: "Achats de marchandises",
  charges_externes: "Charges externes",
  impots_taxes: "Impots et taxes",
  salaires: "Salaires",
  charges_sociales: "Charges sociales",
  dotations_amortissements: "Dotations aux amortissements",
  reintegrations: "Reintegrations fiscales",
  deductions: "Deductions fiscales",
  deficits_anterieurs: "Deficits anterieurs",
} as const;

const FIELD_ALIASES = {
  siren: ["siren"],
  denomination: ["denomination", "raison sociale", "societe", "entreprise"],
  exercice_ouvert: ["exercice ouvert le", "exercice_ouvert", "date ouverture"],
  exercice_clos: ["exercice clos le", "exercice_clos", "date cloture"],
  regime_imposition: ["regime", "regime imposition", "regime d imposition", "type liasse"],
  ca_ht: ["ca ht", "ca", "chiffre affaires ht", "chiffre d affaires ht"],
  capital_social: ["capital social", "capital_social"],
  effectif_moyen: ["effectif moyen", "effectif", "effectif_moyen"],
  capital_pp: ["capital_pp", "capital personnes physiques", "capital detenu 75 personnes physiques"],
  capital_libere: ["capital_libere", "capital libere", "capital entierement libere"],
  resultat_comptable: ["resultat comptable", "resultat_comptable", "resultat"],
  achats_marchandises: ["achats marchandises", "achats_marchandises", "achats"],
  charges_externes: ["charges externes", "charges_externes"],
  impots_taxes: ["impots et taxes", "impots_taxes"],
  salaires: ["salaires"],
  charges_sociales: ["charges sociales", "charges_sociales"],
  dotations_amortissements: ["dotations amortissements", "dotations_amortissements", "amortissements"],
  reintegrations: ["reintegrations fiscales", "reintegrations"],
  deductions: ["deductions fiscales", "deductions"],
  deficits_anterieurs: ["deficits anterieurs", "deficits_anterieurs", "reports deficitaires"],
} as const;

const EXCEL_EXTENSIONS = [".xlsx", ".xls", ".xlsm", ".xlsb"];

const ALIAS_TO_FIELD = new Map<string, keyof typeof LIASSE_2065_FIELD_LABELS>();
Object.entries(FIELD_ALIASES).forEach(([field, aliases]) => {
  aliases.forEach((alias) => {
    ALIAS_TO_FIELD.set(normalizeKey(alias), field as keyof typeof LIASSE_2065_FIELD_LABELS);
  });
});

export type Importable2065FieldKey = keyof typeof LIASSE_2065_FIELD_LABELS;
export type Liasse2065ImportFormValues = Partial<
  Record<Exclude<Importable2065FieldKey, "capital_pp" | "capital_libere">, string>
>;

export interface ParsedLiasse2065Import {
  fileName: string;
  importedFormValues: Liasse2065ImportFormValues;
  capitalPP?: boolean;
  capitalLibere?: boolean;
  matchedFieldKeys: Importable2065FieldKey[];
}

export function get2065ImportFieldLabel(field: Importable2065FieldKey) {
  return LIASSE_2065_FIELD_LABELS[field];
}

export async function parseImported2065File(file: File): Promise<ParsedLiasse2065Import> {
  const imported = buildImportAccumulator();
  const lowerName = file.name.toLowerCase();

  if (hasAnyExtension(lowerName, EXCEL_EXTENSIONS)) {
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
  } else {
    const text = await file.text();
    parseTextContent(text, imported);
  }

  const matchedFieldKeys = Array.from(imported.matched);
  if (matchedFieldKeys.length === 0) {
    throw new Error(
      "Aucun champ 2065/2033 reconnu. Utilisez un fichier JSON, CSV, TXT ou Excel avec des valeurs comme SIREN, denomination, regime, CA HT ou resultat comptable."
    );
  }

  return {
    fileName: file.name,
    importedFormValues: imported.form,
    capitalPP: imported.capitalPP,
    capitalLibere: imported.capitalLibere,
    matchedFieldKeys,
  };
}

function buildImportAccumulator() {
  return {
    form: {} as Liasse2065ImportFormValues,
    capitalPP: undefined as boolean | undefined,
    capitalLibere: undefined as boolean | undefined,
    matched: new Set<Importable2065FieldKey>(),
  };
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
    return;
  }

  if (looksDelimited(trimmed)) {
    const delimiter = detectDelimiter(trimmed);
    const rows = trimmed
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => splitDelimitedLine(line, delimiter));
    parseRows(rows, imported);
    return;
  }

  trimmed
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .forEach((line) => {
      const match = line.match(/^([^:=]+)\s*[:=]\s*(.+)$/);
      if (match) {
        assignRecognizedValue(match[1], match[2], imported);
      }
    });
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
    throw new Error("Le JSON doit contenir un objet avec les champs 2065/2033.");
  }

  collectFromObject(firstObject, imported);
}

function collectFromObject(
  source: Record<string, unknown>,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  Object.entries(source).forEach(([rawKey, rawValue]) => {
    const field = resolveField(rawKey);
    if (field) {
      assignImportedValue(field, rawValue, imported);
      return;
    }

    if (isPlainObject(rawValue)) {
      collectFromObject(rawValue, imported);
    }
  });
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

  normalizedRows.forEach((row) => {
    if (row.length >= 2) {
      assignRecognizedValue(row[0], row[1], imported);
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
  field: Importable2065FieldKey,
  rawValue: unknown,
  imported: ReturnType<typeof buildImportAccumulator>
) {
  if (rawValue == null || rawValue === "") {
    return;
  }

  if (field === "capital_pp" || field === "capital_libere") {
    const parsedBoolean = parseBooleanValue(rawValue);
    if (parsedBoolean == null) {
      return;
    }

    if (field === "capital_pp") {
      imported.capitalPP = parsedBoolean;
    } else {
      imported.capitalLibere = parsedBoolean;
    }
    imported.matched.add(field);
    return;
  }

  if (field === "regime_imposition") {
    const regime = normalizeRegimeValue(rawValue);
    if (!regime) {
      return;
    }
    imported.form[field] = regime;
    imported.matched.add(field);
    return;
  }

  if (field === "siren" || field === "denomination") {
    const textValue = String(rawValue).trim();
    if (!textValue) {
      return;
    }
    imported.form[field] = textValue;
    imported.matched.add(field);
    return;
  }

  if (field === "exercice_ouvert" || field === "exercice_clos") {
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

function normalizeRegimeValue(value: unknown) {
  const normalized = normalizeKey(String(value));
  if (!normalized) {
    return "";
  }

  if (normalized.includes("simplifie") || normalized === "rsi") {
    return "reel_simplifie";
  }

  if (normalized.includes("normal") || normalized === "rn") {
    return "reel_normal";
  }

  return "";
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
  return line.split(delimiter).map((cell) => cell.trim());
}

function shouldTreatAsHeaderTable(rows: string[][]) {
  const recognizedHeaders = rows[0].filter((cell) => resolveField(cell)).length;
  return recognizedHeaders >= 2 || (rows[0].length > 2 && recognizedHeaders >= 1);
}

function hasAnyExtension(fileName: string, extensions: string[]) {
  return extensions.some((extension) => fileName.endsWith(extension));
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
