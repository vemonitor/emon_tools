import { Button } from "@/components/ui/button";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  useZodForm,
} from '@/components/ui/form';
import { Input } from "@/components/ui/input";
import { z } from 'zod';
import { PromiseFormActionType, ArchiveFileEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect } from "react";
import ComboBox from "@/components/form/combo-box";
import { CrudForm } from "@/components/form/crud-form";

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
  handleSubmit: (values: ArchiveFileFormType) => PromiseFormActionType;
  data?: ArchiveFileEdit;
  is_dialog?: boolean,
  successCallBack?: () => void
};

export function ArchiveFileForm({
  handleSubmit,
  data,
  is_dialog,
  successCallBack,
  className
}: ArchiveFileFormProps) {
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

  return (
    <CrudForm
      handleSubmit={handleSubmit}
      data={data}
      queryKeysList={['archive_file']}
      queryKeysEdit={['archive_file_edit']}
      form={form}
      formTitle={"File"}
      is_dialog={is_dialog}
      successCallBack={successCallBack}
      className={className}
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
                url="/api/v1/emon_host/"
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
                url="/api/v1/category/"
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
                url="/api/v1/data_path/"
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
    </CrudForm>
  )
}