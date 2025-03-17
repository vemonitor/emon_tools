export type SubmitHandlerProps = Promise<{ 
    success: boolean,
    act?: "add" | "edit",
    itemId?: string,
    error?: string,
    msg?: string,
    field?: string,
    redirect?: string
 } | void
>

export type BaseActionErrorType = {
    table?: string,
    field?: string,
    error?: string
}

export type AddActionType = Promise<
  void | {
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
>

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
    owner_id?: string
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