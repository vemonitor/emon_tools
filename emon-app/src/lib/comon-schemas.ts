import { z } from "zod";

export const idSchemeIn = z.string()
  .min(1)
  .max(16)
  .regex(/^[0-9]+$/, {
    message: 'Please enter a valid attribute (Only Numeric characters are accepted)',
  })

export const idSchemeOut = z.number()
  .positive();

export const AlphaNumString = z.string()
  .min(1)
  .max(50)
  .regex(/^[A-Za-z0-9]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

export const KeyString = z.string()
  .min(1)
  .max(50)
  .regex(/^[A-Za-z0-9_-]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

export const MailString = z.string()
  .min(1)
  .max(70)
  .email()
  .regex(/^[A-Za-z0-9_@.-]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

export const NameString = z.string()
  .min(1)
  .max(50)
  .regex(/^[A-Za-z0-9_ -]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

export const FileNameString = z.string()
  .min(1)
  .max(50)
  .regex(/^[A-Za-z0-9_.-]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

export const TextString = z.string()
  .min(1)
  .max(50)
  .regex(/^[A-Za-z0-9À-ÖØ-öø-ÿ_ -]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

export const UrlString = z.string()
  .min(1)
  .max(50)
  .regex(/^(https?:\/\/)?([\w-]+\.)?\w{0,6}(\/[\w .-]*)*\/?(\?\w+=\w+)?$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

export const nullableName = z.union([
  z.null(),
  z.string()
    .min(1)
    .max(50)
    .regex(/^[A-Za-zÀ-ÖØ-öø-ÿ ]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    })
  ])