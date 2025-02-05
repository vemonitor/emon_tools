/**
 * utils.ts
 *
 * Helper Utility Class
 */
'use strict';

export default class Ut {
    /**
     * Rounds a number to a specified number of decimal places.
     *
     * @param value - The number to round.
     * @param decimals - The number of decimal places (default: 3). If 0, returns an integer.
     * @param defaultValue - The fallback value if `value` is invalid (default: null).
     * @returns The rounded number or `defaultValue` if input is invalid.
     */
    static roundFloat(value: unknown, decimals: number = 3, defaultValue: number | null = null): number | null {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            return defaultValue;
        }

        const factor = decimals > 0 ? Math.pow(10, decimals) : 1;
        return Math.round(value * factor) / factor;
    }

    /**
     * Fix decimals on a float number.
     * @param fNum - The number to fix decimals.
     * @param fix - The number of decimals.
     * @param defaultValue - The fallback value if input is invalid.
     * @returns The formatted number or `defaultValue` if invalid.
     */
    static toFixedFloat(fNum: unknown, fix: number = 2, defaultValue: unknown = null): number | unknown {
        if (typeof fNum !== "number" || typeof fix !== "number" || !Number.isFinite(fNum)) {
            return defaultValue;
        }
        return parseFloat(fNum.toFixed(fix));
    }

    /** Checks if value is neither null nor undefined */
    static isNotNull(value: unknown): boolean {
        return value !== undefined && value !== null;
    }

    /** Checks if value is not empty (`undefined`, `null`, or an empty string) */
    static isNotEmpty(value: unknown): boolean {
        return Ut.isNotNull(value) && value !== "";
    }

    /** Checks if value is a function */
    static isFunction(value: unknown): value is (...args: unknown[]) => unknown {
        return typeof value === "function";
    }

    /** Checks if value is a valid object */
    static isObject(value: unknown): value is Record<string, unknown> {
        return typeof value === "object" && value !== null && !Array.isArray(value);
    }

    /**
     * Checks if a value is a valid array with optional conditions.
     *
     * @param value - The value to check.
     * @param options - Object with optional conditions:
     *   - notEmpty: Ensures the array is not empty.
     *   - length: Ensures the array has an exact number of elements.
     * @returns True if the value meets the specified conditions, otherwise false.
     */
    static isArray(
        value: unknown,
        options: { notEmpty?: boolean; length?: number } = {}
    ): value is unknown[] {
        if (!Array.isArray(value)) {
            return false;
        }
    
        if (options.notEmpty && value.length === 0) return false;
        if (typeof options.length === "number" && value.length !== options.length) return false;
    
        return true;
    }

    /**
     * Checks if a value is a valid number with optional conditions.
     * 
     * @param value - The value to check.
     * @param options - Object with optional conditions:
     *   - positive: Ensures the number is greater than 0.
     *   - notNull: Ensures the number is not zero.
     *   - nonNeg: Ensures the number is not negative.
     * @returns True if the value meets the specified conditions, otherwise false.
     */
    static isNumber(
        value: unknown, 
        options: { positive?: boolean; notNull?: boolean; nonNeg?: boolean } = {}
    ): value is number {
        if (typeof value !== "number" || !Number.isFinite(value)) {
            return false;
        }
        
        if (options.positive && value <= 0) return false;
        if (options.notNull && value === 0) return false;
        if (options.nonNeg && value < 0) return false;
    
        return true;
    }

    /** Checks if value is a valid string */
    static isStr(value: unknown): value is string {
        return typeof value === "string";
    }

    /** Checks if value is a non-empty string */
    static isStrNotEmpty(value: string | unknown): boolean {
        return Ut.isStr(value) && value.trim().length > 0;
    }

    /** Checks if a key is valid (1-30 chars, alphanumeric & underscore) */
    static isKey(value: unknown): boolean {
        return Ut.isStrNotEmpty(value) && /^[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*$/.test(value as string) && (value as string).length <= 30;
    }

    /** Checks if an attribute key is valid (1-80 chars, alphanumeric, `_`, `-`) */
    static isAttrKey(value: unknown): boolean {
        return Ut.isStrNotEmpty(value) && /^[a-zA-Z0-9]+(?:[_-][a-zA-Z0-9]+)*$/.test(value as string) && (value as string).length <= 80;
    }

    /** Checks if a regex pattern is valid */
    static isValidRegex(regex: unknown): boolean {
        try {
            return Ut.isStr(regex) || regex instanceof RegExp ? new RegExp(regex as string) !== null : false;
        } catch {
            return false;
        }
    }

    /** Converts a timestamp to a locale date string */
    static toLocaleDateFromTime(timeStamp: number): string {
        const dt = new Date(timeStamp * 1000);
        return `${dt.toLocaleDateString()} ${dt.toLocaleTimeString()}`;
    }

    /** Formats bytes to a human-readable size */
    static formatBytes(bytes: number, decimals: number = 2): string {
        if (!bytes) return "0 Bytes";
        const k = 1024, dm = Math.max(0, decimals);
        const sizes = ["Bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }

    /** Adds leading zeros to numbers <= 9 */
    static addLeadingZeros(value: number): string {
        return value <= 9 ? `0${value}` : `${value}`;
    }

    /** Capitalizes the first letter of each word in a string */
    static capitalize(value: unknown, defaultValue: unknown = null): string | unknown {
        if (Ut.isStrNotEmpty(value)) {
            return (value as string).replace(/\b\w/g, (char) => char.toUpperCase());
        }
        return defaultValue;
    }

    /** Retrieves a dictionary key by its value */
    static getDictionaryKeyByValue(object: Record<string, unknown>, value: unknown): string | undefined {
        return Object.keys(object).find((key) => JSON.stringify(object[key]) === JSON.stringify(value));
    }

    /** Filters an object by allowed keys */
    static filterObjectByKey(object: Record<string, unknown>, keys: ReadonlyArray<string>, removeEmpty: boolean = false): Record<string, unknown> {
        return Object.fromEntries(
            Object.entries(object).filter(([key, val]) => keys.includes(key) && (!removeEmpty || Ut.isNotEmpty(val)))
        );
    }
}
