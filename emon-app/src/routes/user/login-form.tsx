import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
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
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router";
import { AlertError, AlertErrorProps } from "@/components/layout/alert-error";
import { useState } from "react";

export const FormScheme = z.object({
  username: z.string()
    .min(1)
    .max(50)
    .regex(/^[A-Za-z0-9-_@.]+$/, {
        message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  }),      
  password: z.string()
    .min(1)
    .max(50)
    .regex(/^[A-Za-z0-9-_@&#çèéàù!]+$/, {
        message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })
});

export type LoginFormType = z.infer<typeof FormScheme>;

// type FormFieldsProps = "username" | "password" | "root" | `root.${string}`;

export type LoginFormProps = React.ComponentPropsWithoutRef<"div"> & {
  className?: string;
};

export function LoginForm({
  className
}: LoginFormProps) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [ alert, setAlert ] = useState<AlertErrorProps | null>(null)
  const form = useZodForm({
      schema: FormScheme,
      defaultValues: {
          username: "",
          password: ''
      },
  });
  
  const onSubmitForm = async (values: LoginFormType) => {
    try {
      await login(values.username, values.password);
      navigate("/dashboard");
    } catch (error) {
      //console.error('Login failed:', error);
      if (error instanceof Error) {
        switch (error.message) {
        case 'Login error':
          setAlert({
            title: 'Login failed',
            message: 'Please verify your credentials and try again.'
          })
          break;
        default:
          setAlert({
            title: 'Login failed',
            message: 'An unknown error occurred.'
          })
        }
      } else {
        console.error('An unknown error occurred:', error);
      }
    }
  }
  return (
    <div className={cn("flex flex-col gap-6", className)}>
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Login</CardTitle>
          <CardDescription>
            Enter your email below to login to your account
          </CardDescription>
          {alert ? (
            <AlertError
              title={alert.title}
              message={alert.message}
            />
          ) : (null)}
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
                  name="username"
                  render={({ field }) => (
                      <FormItem>
                          <FormLabel>UserName</FormLabel>
                          <FormControl>
                              <Input
                                type="email"
                                placeholder="me@example.com"
                                required
                                {...field}
                              />
                          </FormControl>
                          <FormMessage />
                      </FormItem>
                  )}
                />
              </div>
              <div className="grid gap-6">
                <div className="flex items-center">
                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Password</FormLabel>
                            <FormControl>
                                <Input
                                  type="password"
                                  required
                                  {...field}
                                />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                  />
                  
                </div>
                <div className="flex items-center">
                  <a
                      href="#"
                      className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                    >
                      Forgot your password?
                  </a>
                </div>
              </div>
              <Button
                type="submit"
                className="w-full"
              >
                Login
              </Button>
            </div>
            <div className="mt-4 text-center text-sm">
              Don&apos;t have an account?{" "}
              <a href="#" className="underline underline-offset-4">
                Sign up
              </a>
            </div>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}