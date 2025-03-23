import { AlertErrorType, FieldErrorType, FormActionType, FormRequestActionType } from "@/lib/types";


export const requestErrorResponse = (
    response: FormRequestActionType,
    title: string,
    redirect?: string
): FormActionType => {
    const result: FormActionType = {
        success: false
    }
    if (!response.success){
        if(response.errors){
            result.field_errors = response.errors.filter((error) => error.field_name)
                .map((error) => {
                    return {
                        field_name: error.field_name,
                        error: error.error
                    } as FieldErrorType
                });
            result.alert_msgs = response.errors.filter((error) => !error.field_name)
                .map((error) => {
                    return {
                        title: title,
                        error: error.error
                    } as AlertErrorType
                });
        }
        if(response.msg){
            result.toast_msgs = [{
                title: title,
                error: response.msg
            }];
        }
        
        return result;
    }
    return {
        success: true,
        redirect: redirect ? redirect : undefined
    };
}

export const requestCatchError = (
    error: unknown,
    title: string
): FormActionType => {
    console.log(title, error);
    return {
        success: false,
        toast_msgs: [{
            title: title,
            error: 'Internal error'
        }]
    }
}