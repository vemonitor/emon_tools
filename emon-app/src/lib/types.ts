// Type definitions for the emon-app
export type BaseActionErrorType = {
    table?: string,
    field_name?: string,
    error?: string
}

export type FormRequestActionType = {
    success: boolean;
    act?: "add" | "edit";
    itemId?: string;
    from_error?: string;
    error?: string;
    errors?: BaseActionErrorType[];
    msg?: string;
    field?: string;
    redirect?: string;
  }

export type FieldErrorType = {
    field_name: string,
    error: string
}

export type AlertErrorType = {
    title: string,
    error: string
}

export type FormActionType = {
    success: boolean;
    act?: "add" | "edit" | "delete";
    itemId?: string;
    from_error?: string;
    field_errors?: FieldErrorType[];
    alert_msgs?: AlertErrorType[];
    toast_msgs?: AlertErrorType[];
    redirect?: string;
  }

export type PromiseFormActionType = Promise<FormActionType
>

export interface  EditCrudComponentProps<T> {
    row_id?: number
    is_dialog?: boolean,
    successCallBack?: () => void
    data?: T
}

export interface User {
    id: string;
    full_name?: string;
    email: string;
    avatar?: string;
    is_superuser: boolean;
}

export interface UserEdit {
    id?: string;
    full_name?: string;
    email: string;
    avatar?: string;
    is_superuser: boolean;
}

export interface EmonHostBase {
    name: string;
    host?: string;
    api_key?: string;
}

export interface EmonHostView extends EmonHostBase{
    name: string;
    host?: string;
    api_key?: string;
}


export interface EmonHostEdit extends EmonHostBase{
    id?: number;
    created_at?: string;
    updated_at?: string;
    owner_id?: string;
    datapath_id?: number;
}

export interface CategoryBase {
    name: string;
    type: string;
}

export interface CategoryList extends CategoryBase{
    id: number;
    owner_id: string
}

export interface CategoryEdit extends CategoryBase{
    id?: number;
    created_at?: string;
    updated_at?: string;
    owner_id?: string
}

export interface DataPathBase {
    name: string;
    path: string;
}

export interface DataPathList extends DataPathBase{
    id: number;
    owner_id: string
}

export interface DataPathEdit extends DataPathBase{
    id?: number;
    created_at?: string;
    updated_at?: string;
    owner_id?: string;
    path_type: string;
}

export interface ArchiveFileBase {
    name: string;
    file_name: string;
    start_time: string;
    end_time: string;
    interval?: number;
    size?: number;
    npoints?: number;
    feed_id?: number;
    sha_256: string;
}

export interface ArchiveFileList extends ArchiveFileBase{
    id: number;
    owner_id: string
    category_id?: number
    emonhost_id?: number
    emonhost?: {
        id?: number
        name?: string
    }
    category?: {
        id?: number,
        name?: string
    }
}

export interface ArchiveFileEdit extends ArchiveFileBase{
    id?: number;
    created_at?: string;
    updated_at?: string;
    owner_id?: string;
    category_id?: number
    datapath_id?: number
    emonhost_id?: number
}

export interface ProfileBase {
    email: string;
    full_name?: string;
    avatar?: string;
}

export interface ProfileList extends ProfileBase{
    id: string;
}

export interface ProfileEdit extends ProfileBase{
    id?: number;
    created_at?: string;
    updated_at?: string;
}