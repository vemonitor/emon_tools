import { describe, it, expect } from "vitest";
import Ut from "../../src/helpers/utils"; // Adjust the path accordingly

describe("Ut Utility Class", () => {
  describe("isNumber", () => {
    it("should return true for valid numbers", () => {
      expect(Ut.isNumber(10)).toBe(true);
      expect(Ut.isNumber(-5)).toBe(true);
      expect(Ut.isNumber(0)).toBe(true);
    });

    it("should return false for non-numeric values", () => {
      expect(Ut.isNumber("10")).toBe(false);
      expect(Ut.isNumber(null)).toBe(false);
      expect(Ut.isNumber(undefined)).toBe(false);
      expect(Ut.isNumber(NaN)).toBe(false);
      expect(Ut.isNumber(Infinity)).toBe(false);
    });

    it("should handle positive option", () => {
      expect(Ut.isNumber(5, { positive: true })).toBe(true);
      expect(Ut.isNumber(0, { positive: true })).toBe(false);
      expect(Ut.isNumber(-5, { positive: true })).toBe(false);
    });

    it("should handle notNull option", () => {
      expect(Ut.isNumber(10, { notNull: true })).toBe(true);
      expect(Ut.isNumber(0, { notNull: true })).toBe(false);
    });

    it("should handle nonNeg option", () => {
      expect(Ut.isNumber(0, { nonNeg: true })).toBe(true);
      expect(Ut.isNumber(5, { nonNeg: true })).toBe(true);
      expect(Ut.isNumber(-3, { nonNeg: true })).toBe(false);
    });
  });

  describe("isArray", () => {
    it("should return true for valid arrays", () => {
      expect(Ut.isArray([])).toBe(true);
      expect(Ut.isArray([1, 2, 3])).toBe(true);
    });

    it("should return false for non-array values", () => {
      expect(Ut.isArray("string")).toBe(false);
      expect(Ut.isArray(123)).toBe(false);
      expect(Ut.isArray(null)).toBe(false);
      expect(Ut.isArray(undefined)).toBe(false);
    });

    it("should handle notEmpty option", () => {
      expect(Ut.isArray([], { notEmpty: true })).toBe(false);
      expect(Ut.isArray([1], { notEmpty: true })).toBe(true);
    });

    it("should handle length option", () => {
      expect(Ut.isArray([1, 2, 3], { length: 3 })).toBe(true);
      expect(Ut.isArray([1, 2], { length: 3 })).toBe(false);
    });
  });

  describe("roundFloat", () => {
    it("should round numbers to the specified decimal places", () => {
      expect(Ut.roundFloat(3.14159, 2)).toBe(3.14);
      expect(Ut.roundFloat(3.14159, 0)).toBe(3);
      expect(Ut.roundFloat(1.23456)).toBe(1.235);
      expect(Ut.roundFloat(1.234)).toBe(1.234);
      expect(Ut.roundFloat(1.2344)).toBe(1.234);
    });

    it("should return default value for invalid input", () => {
      expect(Ut.roundFloat("test", 2, -1)).toBe(-1);
      expect(Ut.roundFloat(null, 2, "fallback")).toBe("fallback");
    });
  });

  describe("toFixedFloat", () => {
    it("should format numbers with the specified decimals", () => {
      expect(Ut.toFixedFloat(3.14159, 2)).toBe(3.14);
      expect(Ut.toFixedFloat(3.145, 2)).toBe(3.15);
    });

    it("should return default value for invalid input", () => {
      expect(Ut.toFixedFloat("string", 2, "error")).toBe("error");
      expect(Ut.toFixedFloat(null, 2, 0)).toBe(0);
    });
  });

  describe("isStr", () => {
    it("should return true for valid strings", () => {
      expect(Ut.isStr("Hello")).toBe(true);
      expect(Ut.isStr("")).toBe(true);
    });

    it("should return false for non-string values", () => {
      expect(Ut.isStr(123)).toBe(false);
      expect(Ut.isStr(null)).toBe(false);
      expect(Ut.isStr(undefined)).toBe(false);
    });
  });

  describe("isStrNotEmpty", () => {
    it("should return true for non-empty strings", () => {
      expect(Ut.isStrNotEmpty("Hello")).toBe(true);
    });

    it("should return false for empty or non-string values", () => {
      expect(Ut.isStrNotEmpty("")).toBe(false);
      expect(Ut.isStrNotEmpty("   ")).toBe(false);
      expect(Ut.isStrNotEmpty(null)).toBe(false);
      expect(Ut.isStrNotEmpty(123)).toBe(false);
    });
  });

  describe("isKey", () => {
    it("should validate alphanumeric and underscore keys", () => {
      expect(Ut.isKey("valid_key_1")).toBe(true);
      expect(Ut.isKey("Invalid Key")).toBe(false);
      expect(Ut.isKey("a".repeat(31))).toBe(false); // More than 30 chars
    });
  });

  describe("isAttrKey", () => {
    it("should validate keys with underscore and hyphen", () => {
      expect(Ut.isAttrKey("valid-key_1")).toBe(true);
      expect(Ut.isAttrKey("Invalid Key")).toBe(false);
      expect(Ut.isAttrKey("a".repeat(81))).toBe(false); // More than 80 chars
    });
  });

  describe("toLocaleDateFromTime", () => {
    it("should convert timestamp to locale date string", () => {
      const date = new Date(1700000000 * 1000);
      expect(Ut.toLocaleDateFromTime(1700000000)).toBe(`${date.toLocaleDateString()} ${date.toLocaleTimeString()}`);
    });
  });

  describe("formatBytes", () => {
    it("should format bytes to human-readable format", () => {
      expect(Ut.formatBytes(1024)).toBe("1 KiB");
      expect(Ut.formatBytes(1048576)).toBe("1 MiB");
    });

    it("should return '0 Bytes' for 0 input", () => {
      expect(Ut.formatBytes(0)).toBe("0 Bytes");
    });
  });

  describe("capitalize", () => {
    it("should capitalize the first letter of each word", () => {
      expect(Ut.capitalize("hello world")).toBe("Hello World");
      expect(Ut.capitalize("HELLO")).toBe("HELLO");
    });

    it("should return default value for invalid input", () => {
      expect(Ut.capitalize(null, "fallback")).toBe("fallback");
    });
  });

  describe("addLeadingZeros", () => {
    it("should add leading zeros to numbers <= 9", () => {
      expect(Ut.addLeadingZeros(5)).toBe("05");
      expect(Ut.addLeadingZeros(10)).toBe("10");
      expect(Ut.addLeadingZeros(7)).toBe('07');
      expect(Ut.addLeadingZeros(0)).toBe('00');
    });
    it('add_leading_zeros returns the number as a string when two or more digits', () => {
      expect(Ut.addLeadingZeros(10)).toBe('10');
      expect(Ut.addLeadingZeros(123)).toBe('123');
    });
  });

  describe("filterObjectByKey", () => {
    it("should filter an object based on allowed keys", () => {
      const obj = { a: 1, b: 2, c: 3 };
      expect(Ut.filterObjectByKey(obj, ["a", "c"])).toEqual({ a: 1, c: 3 });
    });
  });
});
