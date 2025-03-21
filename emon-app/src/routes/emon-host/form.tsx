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
import { AddActionType, EmonHostEdit } from "@/lib/types";
import { ComponentPropsWithoutRef } from "react";
import ComboBox from "@/components/form/combo-box";
import { CrudForm } from "@/components/form/crud-form";

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

const initFormDefaults = (data?: EmonHostEdit) => {
  return {
    name: data?.name ?? '',
    host: data?.host ?? '',
    api_key: data?.api_key ?? '',
    datapath_id: data?.datapath_id ?? ''
  }
}

export type EmonHostFormProps = ComponentPropsWithoutRef<"div"> & {
  handleSubmit: (values: EmonHostFormType) => AddActionType;
  data?: EmonHostEdit;
  is_dialog?: boolean;
  successCallBack?: () => void;
  className?: string;
};

export function EmonHostForm({
  handleSubmit,
  data,
  is_dialog,
  successCallBack,
  className
}: EmonHostFormProps) {
  const form = useZodForm({
    schema: FormScheme,
    defaultValues: initFormDefaults(data),
  });

  return (
    <CrudForm
      handleSubmit={handleSubmit}
      data={data}
      queryKeysList={['emon_host']}
      queryKeysEdit={['emon_host_edit']}
      form={form}
      formTitle={"Emoncms Host"}
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
                url="/api/v1/data_path/"
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
    </CrudForm>
  )
}