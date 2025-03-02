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
import { AddActionType, ArchiveGroupEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { useQueryClient } from "@tanstack/react-query";

export const FormScheme = z.object({
  name: z.string()
    .min(1)
    .max(15)
    .regex(/^[A-Za-z0-9-_]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
});

export type ArchiveGroupFormType = z.infer<typeof FormScheme>;

type FormFieldsProps = "name" | "root" | `root.${string}`;

const initFormDefaults = (data?: ArchiveGroupEdit) => {
  return {
    id: data?.id ? data.id : 0,
    name: data?.name ?? '',
  }
}

export type ArchiveGroupFormProps = ComponentPropsWithoutRef<"div"> & {
  onSubmit: (values: ArchiveGroupFormType) => AddActionType;
  data?: ArchiveGroupEdit;
  className?: string;
};

export function ArchiveGroupForm({
  onSubmit,
  data,
  className
}: ArchiveGroupFormProps) {
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

  const onSubmitForm = async (values: ArchiveGroupFormType) => {
    const response = await onSubmit(values);

    if (response && response.redirect) {
      form.reset();
      queryClient.invalidateQueries({ queryKey: ['archive_group'] })
      if(data && data.id && data.id > 0){
        queryClient.invalidateQueries({ queryKey: ['archive_group_edit', data.id] })
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
          <CardTitle className="text-2xl">Archive Group</CardTitle>
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
                      <FormLabel>Group</FormLabel>
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