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
import { AddActionType, DataPathEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { useQueryClient } from "@tanstack/react-query";

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

type FormFieldsProps = "name" | "path" | "path_type" | "root" | `root.${string}`;

const initFormDefaults = (data?: DataPathEdit) => {
  return {
    id: data?.id ? data.id : 0,
    name: data?.name ?? '',
    path: data?.path ?? '',
    path_type: data?.path_type ?? '',
  }
}

export type DataPathFormProps = ComponentPropsWithoutRef<"div"> & {
  onSubmit: (values: DataPathFormType) => AddActionType;
  data?: DataPathEdit;
  className?: string;
};

export function DataPathForm({
  onSubmit,
  data,
  className
}: DataPathFormProps) {
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

  const onSubmitForm = async (values: DataPathFormType) => {
    const response = await onSubmit(values);

    if (response && response.redirect) {
      form.reset();
      queryClient.invalidateQueries({ queryKey: ['data_path'] })
      if(data && data.id && data.id > 0){
        queryClient.invalidateQueries({ queryKey: ['data_path_edit', data.id] })
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
          <CardTitle className="text-2xl">DataPath</CardTitle>
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
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}