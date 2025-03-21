import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { idSchemeIn, idSchemeOut } from "./comon-schemas"

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

export const validateStringId = (item_id?: string) => {
  const validateIn = idSchemeIn.safeParse(item_id);
  const validateOut = idSchemeOut.safeParse(Number(item_id));
  return validateIn.success === true && validateOut.success === true ? Number(item_id) : 0;
}

export const validateId = (item_id?: string) => {
  const validateIn = idSchemeIn.safeParse(item_id);
  const validateOut = idSchemeOut.safeParse(Number(item_id));
  return validateIn.success === true && validateOut.success === true ? Number(item_id) : 0;
}

export const validateIds = (route_id?: string, props_id?: number): number => {
  const validateRoute = validateId(route_id);
  const validateProps = idSchemeOut.safeParse(props_id);
  if(validateProps.success === true){
    return props_id ? props_id : 0
  }
  return validateRoute > 0 ? validateRoute : 0;
}
