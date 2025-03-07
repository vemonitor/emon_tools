import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  useZodForm,
} from '@/components/ui/form';
import { Input } from "@/components/ui/input";
import { z } from 'zod';
import { AddActionType, EmonHostEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { useQueryClient } from "@tanstack/react-query";
import ComboBox from "@/components/form/combo-box";

export const FormScheme = z.object({
  name: z.string()
    .min(1)
    .max(15)
    .regex(/^[A-Za-z0-9-_ ]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
  datapath_id: z.union(
    [
      z.null(),
      z.string()
        .regex(/^[0-9]+$/, {
          message: 'Invalid Value must be an integer',
        }),
      z.number()
        .positive()
    ]
  ),
  host: z.string()
    .url({ message: "Invalid url" })
    .min(1)
    .max(50),
  api_key: z.string()
    .min(1)
    .max(50)
    .regex(/^[A-Za-z0-9-_]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    })
});

export type EmonHostFormType = z.infer<typeof FormScheme>;

type FormFieldsProps = "name" | "host" | "api_key" | "datapath_id" | "root" | `root.${string}`;

const initFormDefaults = (data?: EmonHostEdit) => {
  return {
    id: data?.id ? data.id : 0,
    name: data?.name ?? '',
    host: data?.host ?? '',
    api_key: data?.api_key ?? '',
    datapath_id: data?.datapath_id ?? ''
  }
}

export type EmonHostFormProps = ComponentPropsWithoutRef<"div"> & {
  onSubmit: (values: EmonHostFormType) => AddActionType;
  data?: EmonHostEdit;
  className?: string;
};

export function EmonHostForm({
  onSubmit,
  data,
  className
}: EmonHostFormProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient()
  const form = useZodForm({
    schema: FormScheme,
    defaultValues: initFormDefaults(data),
  });

  // Reset the form whenever new data arrives
  useEffect(() => {
    if (data) {
      form.reset(initFormDefaults(data));
    }
  }, [data, form]);

  const onSubmitForm = async (values: EmonHostFormType) => {
    const response = await onSubmit(values);

    if (response && response.redirect) {
      form.reset();
      queryClient.invalidateQueries({ queryKey: ['category'] })
      if(data && data.id && data.id > 0){
        queryClient.invalidateQueries({ queryKey: ['category_edit', data.id] })
      }
      navigate(response.redirect);
    }
    else if (response && response.errors && response.errors.length > 0) {
      response.errors.map(obj => {
        form.setError(
          obj.field_name as FormFieldsProps,
          { type: 'manual', message: obj.error }
        )
      })
    }
    else if (response && response.error) {
      console.log(response.error);
    }
    else {
      console.log("Fatal error");
    }
    return;
  }

  return (
    <div className={cn("flex flex-col gap-6", className)}>
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Emon Host</CardTitle>
        </CardHeader>
        <CardContent>
          <Form
            className=""
            form={form}
            onSubmit={onSubmitForm}
          >
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Host Name</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="EmonLocal"
                          required
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="datapath_id"
                  render={({ field }) => (
                    <ComboBox
                      name="datapath_id"
                      label="Data Path"
                      description="Related Data Files Path."
                      url="http://127.0.0.1:8000/api/v1/data_path/"
                      queryKey={['data_path']}
                      resultKeyLabel="name"
                      resultKeyValue="id"
                      form={form}
                      field={field}
                    />  
                  )}
                />
                <FormField
                  control={form.control}
                  name="host"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Emoncms Host</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="http://127.0.0.1:8080"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="api_key"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Emoncms Api Key</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <Button
                type="submit"
                className="w-full"
              >
                Submit
              </Button>
            </div>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}