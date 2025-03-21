import { Button } from "@/components/ui/button";
import {
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
import { AddActionType, DataPathEdit } from "@/lib/types";
import { ComponentPropsWithoutRef } from "react";
import { CrudForm } from "@/components/form/crud-form";

export const FormScheme = z.object({
  name: z.string()
    .min(1)
    .max(30)
    .regex(/^[A-Za-z0-9-_ ]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
  path: z.string()
    .min(1)
    .max(255)
    .regex(/^[A-Za-z0-9-_/\\:]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
  path_type: z.string()
    .min(1)
    .max(30)
    .regex(/^[A-Za-z0-9-_]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
});

export type DataPathFormType = z.infer<typeof FormScheme>;

const initFormDefaults = (data?: DataPathEdit) => {
  return {
    name: data?.name ?? '',
    path: data?.path ?? '',
    path_type: data?.path_type ?? '',
  }
}

export type DataPathFormProps = ComponentPropsWithoutRef<"div"> & {
  handleSubmit: (values: DataPathFormType) => AddActionType;
  data?: DataPathEdit;
  is_dialog?: boolean;
  successCallBack?: () => void;
  className?: string;
};

export function DataPathForm({
  handleSubmit,
  data,
  is_dialog,
  successCallBack,
  className
}: DataPathFormProps) {
  const form = useZodForm({
    schema: FormScheme,
    defaultValues: initFormDefaults(data),
  });

  return (
    <CrudForm
      handleSubmit={handleSubmit}
      data={data}
      queryKeysList={['data_path']}
      queryKeysEdit={['data_path_edit']}
      form={form}
      formTitle={"Data Path"}
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
            name="path_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Type</FormLabel>
                <FormControl>
                  <Select
                    defaultValue={field?.value ? field?.value : "null"}
                    onValueChange={field.onChange}
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        <SelectItem value="null">Undefined</SelectItem>
                        <SelectItem value="archives">Archives</SelectItem>
                        <SelectItem value="emoncms">Emoncms</SelectItem>
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="path"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Path</FormLabel>
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