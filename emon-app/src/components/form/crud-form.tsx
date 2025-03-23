import { useQueryClient } from "@tanstack/react-query";
import { PropsWithChildren, useState } from "react";
import { useNavigate } from "react-router";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Form,
} from '@/components/ui/form';
import { PromiseFormActionType } from "@/lib/types";
import { cn } from "@/lib/utils";
import { FieldValues, UseFormReturn } from "react-hook-form";
import { AlertError, AlertErrorProps } from "../layout/alert-error";
import { useToast } from "@/hooks/use-toast";

export type CrudFormProps<T1 extends FieldValues, T2> = PropsWithChildren & {
    handleSubmit: (values: T1) => PromiseFormActionType;
    data?: T2;
    queryKeysList: string[];
    queryKeysEdit: string[];
    form: UseFormReturn<T1>;
    formTitle: string;
    //initFormDefaults: (data?: T2) => DefaultValues<T1>;
    is_dialog?: boolean;
    successCallBack?: () => void;
    className?: string;
};

export type FormFieldsProps = "root" | `root.${string}`;

export function CrudForm<T1 extends FieldValues, T2>({
    handleSubmit,
    data,
    queryKeysList,
    queryKeysEdit,
    form,
    formTitle,
    //initFormDefaults,
    is_dialog,
    successCallBack,
    children,
    className
}: CrudFormProps<T1, T2>) {
    const navigate = useNavigate();
    const queryClient = useQueryClient()
    const [ alert, setAlert ] = useState<AlertErrorProps | null>(null)
    const {toast} = useToast()
    const onSubmitForm = async (values: T1) => {
        const response = await handleSubmit(values);

        if (response && response.success && response.redirect) {
            form.reset();
            queryClient.invalidateQueries({ queryKey: queryKeysList })
            if (data) {
                queryClient.invalidateQueries({ queryKey: queryKeysEdit })
            }
            if (is_dialog === true && successCallBack) {
                successCallBack()
            }
            else { navigate(response.redirect); }
        }
        else if (response && response.field_errors && response.field_errors.length > 0) {
            response.field_errors.map(obj => {
                form.setError(
                    obj.field_name as FormFieldsProps,
                    { type: 'manual', message: obj.error }
                )
            })
            console.log('Fields Errors: ', response.field_errors);
        }
        else if (response && response.alert_msgs && response.alert_msgs.length > 0) {
            response.alert_msgs.map(obj => {
                setAlert({
                    title: obj.title,
                    message: obj.error
                })
            })
            console.log('Alert messages: ', response.alert_msgs);
        }
        else if (response && response.toast_msgs && response.toast_msgs.length > 0) {
            response.toast_msgs.map(obj => {
                toast({
                    title: obj.title,
                    description: obj.error
                })
            })
            console.log("Fatal error");
        }
        else{
            console.error("Fatal error: Unknown Form error...");
        }
        return;
    }
    return (
        <div className={cn("flex flex-col gap-6", className)}>
            <Card>
                <CardHeader>
                    <CardTitle className="text-2xl">{formTitle}</CardTitle>
                    {alert ? (
                        <AlertError
                            title={alert.title}
                            message={alert.message}
                        />
                    ) : (null)}
                </CardHeader>
                <CardContent>
                    <Form
                        className=""
                        form={form}
                        onSubmit={onSubmitForm}
                    >
                        {children}
                    </Form>
                </CardContent>
            </Card>
        </div>
    )
}
