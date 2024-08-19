variable "hwc_access_key" {
  type        = string
  description = "Access Key (AK) of your Huawei Cloud account or IAM User"
}

variable "hwc_secret_key" {
  type        = string
  sensitive   = true
  description = "Secret Access Key (SK) of your Huawei Cloud account or IAM User"
}

variable "region" {
  type        = string
  description = "Region where cloud resources will be deployed by default"
}
