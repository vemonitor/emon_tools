import { cn } from "@/lib/utils";
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
import { AddActionType, CategoryEdit } from "@/lib/types";
import { ComponentPropsWithoutRef } from "react";
import { CrudForm } from "@/components/form/crud-form";
import { KeyString, NameString } from "@/lib/comon-schemas";

export const FormScheme = z.object({
  name: NameString,
  type: KeyString,
});

export type CategoryFormType = z.infer<typeof FormScheme>;

const initFormDefaults = (data?: CategoryEdit) => {
  return {
    name: data?.name ?? '',
    type: data?.type ?? '',
  }
}

//export type CategoryFormProps = ComponentPropsWithoutRef<"div"> & CrudFormProps<CategoryFormType, CategoryEdit>;
export type CategoryFormProps = ComponentPropsWithoutRef<"div"> & {
  handleSubmit: (values: CategoryFormType) => AddActionType;
  data?: CategoryEdit;
  is_dialog?: boolean;
  successCallBack?: () => void;
  className?: string;
};

export function CategoryForm({
  handleSubmit,
  data,
  is_dialog,
  successCallBack,
  className
}: CategoryFormProps) {
  
  const form = useZodForm({
      schema: FormScheme,
      defaultValues: initFormDefaults(data),
    });
  // initFormDefaults={initFormDefaults}
  return (
    <div className={cn("flex flex-col gap-6", className)}>
      <CrudForm
        handleSubmit={handleSubmit}
        data={data}
        queryKeysList={['category']}
        queryKeysEdit={['category_edit']}
        form={form}
        formTitle={"Category"}
        is_dialog={is_dialog}
        successCallBack={successCallBack}
        className={className}
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
          
      </CrudForm>
    </div>
  )
}