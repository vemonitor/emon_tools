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
    Avatar,
    AvatarFallback,
    AvatarImage,
} from "@/components/ui/avatar"
import { Input } from "@/components/ui/input";
import { z } from 'zod';
import { PromiseFormActionType, User, UserEdit } from "@/lib/types";
import { ComponentPropsWithoutRef, useEffect, useRef } from "react";
import { FileNameString, MailString, TextString } from "@/lib/comon-schemas";
import { CrudForm } from "@/components/form/crud-form";
import { getImagePath } from "@/lib/utils";

export const FormScheme = z.object({
  full_name: z.optional(TextString),
  email: MailString,
  avatar: z.optional(FileNameString),
  file: z.instanceof(File).optional()
});

export type ProfileFormType = z.infer<typeof FormScheme>;


const initFormDefaults = (data?: UserEdit) => {
  return {
    full_name: data?.full_name ?? '',
    email: data?.email ?? '',
    avatar: data?.avatar ?? '',
    file: undefined
  }
}

export type ProfileFormProps = ComponentPropsWithoutRef<"div"> & {
  handleSubmit: (values: ProfileFormType) => PromiseFormActionType;
  data: User;
  is_dialog?: boolean,
  successCallBack?: () => void
  className?: string;
};

export function ProfileForm({
  handleSubmit,
  data,
  is_dialog,
  successCallBack,
  className
}: ProfileFormProps) {
  const form = useZodForm({
    schema: FormScheme,
    defaultValues: initFormDefaults(data),
  });
  // Reference for the hidden file input
  const fileInputRef = useRef<HTMLInputElement>(null);
  // Watch the file field for previewing the image.
  const newAvatarFile = form.watch("file");
  // If a new file is selected, create a preview URL; otherwise, use the current avatar.
  const imagePath = newAvatarFile
    ? URL.createObjectURL(newAvatarFile)
    : getImagePath(form.getValues("avatar"));

  // Clean up object URL when the component unmounts or new file is selected
  useEffect(() => {
    if (newAvatarFile) {
      const objectUrl = URL.createObjectURL(newAvatarFile);
      return () => URL.revokeObjectURL(objectUrl);
    }
  }, [newAvatarFile]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
  
    // Validate file type and size
    const validTypes = ["image/jpeg", "image/png", "image/gif"];
    if (!validTypes.includes(file.type)) {
      alert("Unsupported file type. Please select a JPEG, PNG, or GIF image.");
      return;
    }
    if (file.size > 2 * 1024 * 1024) { // example: limit to 2MB
      alert("File is too large. Please select a file under 2MB.");
      return;
    }
    
    form.setValue("file", file);
  };

  return (
    <CrudForm
      handleSubmit={handleSubmit}
      data={data}
      queryKeysList={['users']}
      queryKeysEdit={['profile_edit']}
      form={form}
      formTitle={"Profile"}
      is_dialog={is_dialog}
      successCallBack={successCallBack}
      className={className}
    >
      <div className="flex flex-col gap-6">
        <div className="grid gap-2">
          <FormField
            control={form.control}
            name="full_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Full Name</FormLabel>
                <FormControl>
                  <Input
                    type="text"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    type="text"
                    required
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormItem>
            <FormLabel>Avatar</FormLabel>
            <div className="flex items-center gap-4">
              <Avatar className="h-40 w-40 rounded-full">
                <AvatarImage src={imagePath || "/placeholder.png"} alt={data.full_name} />
                <AvatarFallback className="rounded-lg">CN</AvatarFallback>
              </Avatar>
              <Button
                variant="outline"
                type="button"
                onClick={() => fileInputRef.current?.click()}
              >
                Change Avatar
              </Button>
              {/* Hidden file input */}
              <input
                type="file"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileChange}
              />
            </div>
          </FormItem>
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