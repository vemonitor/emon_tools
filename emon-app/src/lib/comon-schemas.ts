import { z } from "zod";

export const idSchemeIn = z.string()
  .min(1)
  .max(16)
  .regex(/^[0-9]+$/, {
    message: 'Please enter a valid attribute (Only Numeric characters are accepted)',
  })

export const idSchemeOut = z.number()
  .positive();