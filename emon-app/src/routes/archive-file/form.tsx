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
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";

import { Input } from "@/components/ui/input";
import { z } from 'zod';
import { AddActionType, ArchiveFileEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { useQueryClient } from "@tanstack/react-query";
import ComboBox from "@/components/form/combo-box";

export const FormScheme = z.object({
  name: z.string()
    .min(1)
    .max(40)
    .regex(/^[A-Za-z0-9-_ ]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
  file_name: z.string()
    .min(1)
    .max(40)
    .regex(/^[A-Za-z0-9-_.]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
  category_id: z.union(
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
  emonhost_id: z.union(
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
});

export type ArchiveFileFormType = z.infer<typeof FormScheme>;

type FormFieldsProps = "name" | "file_name" | "category_id" | "emonhost_id" | "datapath_id" | "root" | `root.${string}`;

const initFormDefaults = (data?: ArchiveFileEdit) => {
  return {
    name: data?.name ?? '',
    file_name: data?.file_name ?? '',
    category_id: data?.category_id ? Number(data.category_id) : 0,
    datapath_id: data?.datapath_id ? Number(data.datapath_id) : 0,
    emonhost_id: data?.emonhost_id ? Number(data.emonhost_id) : 0,
  }
}

export type ArchiveFileFormProps = ComponentPropsWithoutRef<"div"> & {
  onSubmit: (values: ArchiveFileFormType) => AddActionType;
  data?: ArchiveFileEdit;
  is_dialog?: boolean,
  successCallBack?: () => void
};

export function ArchiveFileForm({
  onSubmit,
  data,
  is_dialog,
  successCallBack,
  className
}: ArchiveFileFormProps) {
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

  const onSubmitForm = async (values: ArchiveFileFormType) => {
    const response = await onSubmit(values);

    if (response && response.redirect) {
      form.reset();
      queryClient.invalidateQueries({ queryKey: ['archive_group'] })
      if(data && data.id && data.id > 0){
        queryClient.invalidateQueries({ queryKey: ['archive_group_edit', data.id] })
      }
      if(is_dialog === true && successCallBack){
        successCallBack()
      }
      else{navigate(response.redirect);}
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
          <CardTitle className="text-2xl">Archive File</CardTitle>
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
                      <FormLabel>Name</FormLabel>
                      <FormControl>
                        <Input
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
                  name="file_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>File Name</FormLabel>
                      <FormControl>
                        <Input
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
                  name="emonhost_id"
                  render={({ field }) => (
                    <ComboBox
                      name="emonhost_id"
                      label="Emon Host"
                      description="Emoncms host server"
                      queryKey={['emonhost']}
                      url="http://127.0.0.1:8000/api/v1/emon_host/"
                      resultKeyLabel="name"
                      resultKeyValue="id"
                      form={form}
                      field={field}
                    />
                  )}
                />
                <FormField
                  control={form.control}
                  name="category_id"
                  render={({ field }) => (
                    <ComboBox
                      name="category_id"
                      label="Category"
                      description="File Category"
                      queryKey={['category']}
                      url="http://127.0.0.1:8000/api/v1/category/"
                      resultKeyLabel="name"
                      resultKeyValue="id"
                      form={form}
                      field={field}
                    />
                  )}
                />
                <FormField
                  control={form.control}
                  name="datapath_id"
                  render={({ field }) => (
                    <ComboBox
                      name="datapath_id"
                      label="Server Path"
                      description="Path"
                      queryKey={['datapath']}
                      url="http://127.0.0.1:8000/api/v1/data_path/"
                      resultKeyLabel="name"
                      resultKeyValue="id"
                      form={form}
                      field={field}
                    />
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