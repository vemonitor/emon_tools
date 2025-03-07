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
import { AddActionType, CategoryEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { useQueryClient } from "@tanstack/react-query";

export const FormScheme = z.object({
  name: z.string()
    .min(1)
    .max(40)
    .regex(/^[A-Za-z0-9-_ ]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
  type: z.string()
    .min(1)
    .max(30)
    .regex(/^[A-Za-z0-9-_]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
});

export type CategoryFormType = z.infer<typeof FormScheme>;

type FormFieldsProps = "name" | "type" | "root" | `root.${string}`;

const initFormDefaults = (data?: CategoryEdit) => {
  return {
    id: data?.id ? data.id : 0,
    name: data?.name ?? '',
    type: data?.type ?? '',
  }
}

export type CategoryFormProps = ComponentPropsWithoutRef<"div"> & {
  onSubmit: (values: CategoryFormType) => AddActionType;
  data?: CategoryEdit;
  className?: string;
};

export function CategoryForm({
  onSubmit,
  data,
  className
}: CategoryFormProps) {
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

  const onSubmitForm = async (values: CategoryFormType) => {
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
          <CardTitle className="text-2xl">Category</CardTitle>
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
                name="type"
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
                                <SelectItem value="fina_files">Fina Files</SelectItem>
                                <SelectItem value="fina_paths">Fina Paths</SelectItem>
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
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Category</FormLabel>
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