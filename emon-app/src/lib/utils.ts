import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { idSchemeIn } from "./comon-schemas"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const getImagePath = (imgName?: string) => {
  const imgPath = import.meta.env.VITE_IMAGES_URL
  return imgPath && imgName ? `${imgPath}/${imgName}` : undefined;
}

export const getApiUrl = (url?: string) => {
  const baseUrl = import.meta.env.VITE_API_URL
  return baseUrl && url ? `${baseUrl}${url}` : '';
}

export const validateId = (item_id?: string) => {
  const validate = idSchemeIn.safeParse(item_id);
  if(validate.success === true)
  return validate.success === true ? Number(item_id) : undefined;
}