/**
 * utils.js
 * 
 */
'use strict';

/**
 * Helper Utilities
 * @type {{isObject: (function(*): *), isNumber: (function(*): *), isPositiveNumber: (function(*): *), isArray: (function(*): arg is any[]), isStr: (function(*): *)}}
 */
export default class Ut{
    /**
     * Fix decimals on float number
     * @param fNum {number | undefined | null} The number to fix decimals
     * @param fix {number} The number of decimals
     * @param defaultValue {number | undefined | null} The default value to be returned if any params is not valid
     * @return {number | undefined | null} Return float number with fixed decimals or value of defaultValue
     */
    static toFixedFloat (
        fNum: number | undefined | null,
        fix: number = 2,
        defaultValue: number | undefined | null = null
        ): number | undefined | null {
        return (
                fNum && Ut.isNumber(fNum)
                && Ut.isNumber(fix)
            ) ? parseFloat(fNum.toFixed(fix)) : defaultValue;
    }

    /**
     * Test if value is not null or undefined
     * @param value {*} The value to test
     * @return {boolean} Return true if value is a valid number
     */
    static isNotNull (value: any): boolean {
        return (
                (value || value === 0)
                && value !== undefined && value !== null
            ) ? true : false
    }

    /**
     * Test if value is not empty [undefined, null or '']
     * @param value {*} The value to test
     * @returns {boolean} True if value is not empty
     */
    static isNotEmpty(value: any): boolean{
        return Ut.isNotNull(value) && value !== ''
    }

    /**
     * Test if value is a valid function
     * @param value {Function | null | undefined} The value to test
     * @return {boolean} Return true if value is a valid function
     */
    static isFunction(value: Function | null | undefined): boolean{
        return Ut.isNotNull(value) && typeof value === "function" 
    }
    /**
     * Test if value is a valid object
     * @param value {object | null | undefined} The value to test
     * @return {boolean} Return true if value is a valid object
     */
    static isObject (value: object | null | undefined): boolean {
        return Ut.isNotNull(value)
            && typeof value === 'object'
            && !Array.isArray(value)
    }
    
    /**
     * Test if value is a valid array
     * @param value {any[] | null | undefined} The value to test
     * @return {boolean} Return true if value is a valid array
     */
    static isArray (value: any[] | null | undefined): boolean {
        return Ut.isNotNull(value) && Array.isArray(value)
    }

    /**
     * Test if value is a valid array
     * @param value {any[] | null | undefined} The value to test
     * @return {boolean} Return true if value is a valid array
     */
    static isArrayNotEmpty (value: any[] | null | undefined): boolean {
        return (
            value && Ut.isArray(value) && value.length > 0
            ) ? true : false;
    }

    /**
     * Test if value is a number
     * @param value {number | undefined | null} The value to test
     * @return {boolean} Return true if value is a valid number
     */
    static isNumber(value: number | undefined | null): boolean {
        
        return (
                (value || value === 0)
                && Ut.isNotNull(value)
                && !isNaN(value)
            ) ? true : false;
    }
    /**
     * Test if value is a positive number
     * @param value {number | undefined | null} The value to test
     * @return {boolean} Return true if value is a valid positive number
     */
    static isPositiveNumber (value: number | undefined | null): boolean {
        return (
                (value || value === 0)
                && Ut.isNumber(value)
                && value > 0
            ) ? true : false
    }

    /**
     * Test if value is a number different of zero
     * @param value {number | undefined | null} The value to test
     * @return {boolean} Return true if value is a valid positive number
     */
    static isNumberNotNull (value: number | undefined | null): boolean {
        return (
                (value)
                && Ut.isNumber(value)
            ) ? true : false
    }

    /**
     * Test if value is a valid string
     * @param value {any} The value to test
     * @return {boolean} Return true if value is a valid string
     */
    static isStr (value: any): boolean{
        return (typeof value === 'string' || value instanceof String)
    }
    /**
     * Test if value is a valid string and his not empty
     * @param value {string | object | undefined | null} The value to test
     * @return {boolean} Return true if value is a valid string and his not empty
     */
    static isStrNotEmpty (
        value: string | object | undefined | null
        ): boolean {
        return (Ut.isNotEmpty(value) && Ut.isStr(value))
    }
    /**
     * Test if value is a valid key and his not empty.
     * A key must :
     *  - have a length between 1 and 30 chars
     *  - start and end with alphanumerical character
     *  - contain alphanumerical character and '_'
     * @param value {string | undefined | null} The value to test
     * @return {boolean} Return true if value is a valid key
     */
    static isKey (value: string | undefined | null): boolean {
        return (
            value 
            && Ut.isStrNotEmpty(value)
            && /(?=\w{1,30}$)^([a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*)$/.test(value)
            ) ? true : false;
    }
    /**
     * Test if value is a valid Attribute key.
     * A key must :
     *  - have a length between 1 and 80 chars
     *  - start and end with alphanumerical character
     *  - contain alphanumerical character and '_' or '-'
     * @param value {string | undefined | null} The value to test
     * @return {boolean} Return true if value is a valid Attribute key
     */
    static isAttrKey (value: string | undefined | null): boolean {
        return (
            value
            && Ut.isStrNotEmpty(value) 
            && /(?=[a-zA-Z0-9\-_]{1,80}$)^([a-zA-Z0-9]+(?:[_-][a-zA-Z0-9]+)*)$/.test(value)
            ) ? true : false;
    }
    /**
     * Test is regex is valid
     * @param regex {RegExp|string} The regex to test
     * @return {boolean} Return true if regex is valid or false else where.
     */
    static isValidRegex (
        regex: string | RegExp | undefined | null
        ): boolean {
        if(regex && Ut.isNotNull(regex)){
            new RegExp(regex);
            return true
        }
        return false
    }

    static toLocaleDateFromTime(timeStamp: number): string{
        const dt = new Date(timeStamp * 1000)
        return `${dt.toLocaleDateString()} ${dt.toLocaleTimeString()}`
    }

    static formatBytes(
        bytes: number,
        decimals: number = 2
    ) {
        if (!+bytes) return '0 Bytes'
    
        const k = 1024
        const dm = decimals < 0 ? 0 : decimals
        const sizes = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    
        const i = Math.floor(Math.log(bytes) / Math.log(k))
    
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
    }
    /**
     * Capitalize first letter from all words in text
     * @param {string | undefined | null} value The string to capitalize
     * @param {*} defaultValue The default value to return if invalid string is set
     * @returns {string | *} Return Capitalized string or defaultValue if string is invalid
     */
    static capitalize(
        value: string | undefined | null,
        defaultValue: any=null
        ): string | any {
        if(value && Ut.isStrNotEmpty(value)){
            const arr = value.split(" ")
            const capArr = arr.map((val: string) => {
                return val.charAt(0).toUpperCase() + val.slice(1)
            })
            return capArr.join(" ")
        }
        return defaultValue
    }
    /**
     * Get key by value from object
     * 
     * @param {object} object The source object
     * @param {object | [] | string | number} value The object value to search
     * @returns {any} The first object key retrieved from value or undefined if value is not retrived.
     */
    static getDictionaryKeyByValue(
            object: { [x: string]: any; },
            value: any
        ): any{
        if(Ut.isObject(object)){
            return Object.keys(object).find(key => {
                if(Ut.isObject(value) || Ut.isArray(value)){
                    return JSON.stringify(object[key]) === JSON.stringify(value)
                }else{
                    return object[key] === value
                }
            });
        }
    }
    /**
     * Filter object by array keys
     * @param {object} object The source object
     * @param {[{string}]} value The object value to search
     * @param {boolean} removeEmptyValues Set if empty values must be removed from result
     * @returns {{*} | undefined} The filtered object or undefined if value is not retrived or bad properties set.
     */
    static filterObjectByKey(
            object: { [x: string]: any; },
            keys: string[],
            removeEmptyValues:boolean=false
        ): object | undefined{
        if(Ut.isObject(object) && Ut.isArrayNotEmpty(keys)){
            return Object.keys(object).reduce(
                (res: {[key: string]: string | undefined}, key:string) => {
                const withEmptyValues = !removeEmptyValues 
                    || (removeEmptyValues === true && Ut.isNotEmpty(object[key]))
                if(keys.includes(key)
                    && withEmptyValues){
                    res[key] = object[key]
                }
                return res;
            }, {});
        }
    }
}