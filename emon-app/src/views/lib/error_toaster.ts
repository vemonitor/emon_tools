import Ut from "@/helpers/utils"

export type reqResultType = {[key: string]: string | boolean | number}
export type errorType = {name: string, message: string}
export type toastErrorsOut = {
  title: string
  description: string
}

export const toastErrors = (
  data: reqResultType[],
  errors: errorType[],
  title: string
): toastErrorsOut | undefined => {
  let data_errors: toastErrorsOut[] = []
  if(Ut.isArray(data) && data.length > 0){
    data_errors = data
      .filter(obj => Ut.isObject(obj) && obj.hasOwnProperty('success') ? obj.success === false : false)
      .reduce((result:  toastErrorsOut[], obj) => {
        result.push({
          title: "PhpFina Meta Error: ",
          description: obj.error.toString()
        })
        return result
      }, [])
  }
  if(Ut.isArray(errors) && errors.length > 0){
    const raised_errors = errors.map((obj) => {
      return {
        title: "PhpFina Meta Error - " + obj.name,
        description: obj.message
      }
    })
    data_errors = data_errors.concat(raised_errors).flat()
  }
  if(data_errors.length > 0){
    return data_errors.reduce((result, obj) => {
      result.description += obj.description + "<br />"
      return result
    }, {title: title, description: ""})
  }
  return;
}