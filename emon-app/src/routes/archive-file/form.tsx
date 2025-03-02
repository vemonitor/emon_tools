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
import { AddActionType, ArchiveFileEdit, ArchiveGroupEdit, EmonHostEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { useQueryClient } from "@tanstack/react-query";

export const FormScheme = z.object({
  name: z.string()
    .min(1)
    .max(15)
    .regex(/^[A-Za-z0-9-_ ]+$/, {
      message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
    }),
  archivegroup_id: z.union(
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

type FormFieldsProps = "name" | "archivegroup_id" | "emonhost_id" | "root" | `root.${string}`;

const initFormDefaults = (data?: ArchiveFileEdit) => {
  return {
    id: data?.id ? data.id : 0,
    name: data?.name ?? '',
    archivegroup_id: data?.archivegroup_id ? Number(data.archivegroup_id) : 0,
    emonhost_id: data?.emonhost_id ? Number(data.emonhost_id) : 0,
  }
}

export type ArchiveFileFormProps = ComponentPropsWithoutRef<"div"> & {
  onSubmit: (values: ArchiveFileFormType) => AddActionType;
  data?: ArchiveFileEdit;
  archiveGroups: ArchiveGroupEdit[];
  emonHosts: EmonHostEdit[]
  className?: string;
};

export function ArchiveFileForm({
  onSubmit,
  data,
  archiveGroups,
  emonHosts,
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
                      <FormLabel>Group Name</FormLabel>
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
                  name="emonhost_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Emon Host</FormLabel>
                      <FormControl>
                        <Select
                            defaultValue={field?.value ? field?.value.toString() : "0"}
                            onValueChange={field.onChange}
                        >
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Emoncms Host" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectGroup>
                                  <SelectItem value="0">Undefined</SelectItem>
                                    {emonHosts && (emonHosts.map((value, index) => {
                                      return (
                                        <SelectItem key={index} value={`${value.id??0}`}>{value.name}</SelectItem>
                                      )
                                    }))}
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
                  name="archivegroup_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Group</FormLabel>
                      <FormControl>
                        <Select
                            defaultValue={field?.value ? field?.value.toString() : "0"}
                            onValueChange={field.onChange}
                        >
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Group" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectGroup>
                                  <SelectItem value="0">Undefined</SelectItem>
                                    {archiveGroups && (archiveGroups.map((value, index) => {
                                      return (
                                        <SelectItem key={index} value={`${value.id??0}`}>{value.name}</SelectItem>
                                      )
                                    }))}
                                </SelectGroup>
                            </SelectContent>
                        </Select>
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