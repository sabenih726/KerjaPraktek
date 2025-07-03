"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Upload,
  FileText,
  Download,
  Loader2,
  CheckCircle,
  XCircle,
  Copy,
  AlertCircle,
  FileSpreadsheet,
  FolderOpen,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface ExtractedData {
  [key: string]: any
}

interface ResultItem {
  filename: string
  status: "success" | "error"
  data?: ExtractedData
  error?: string
}

interface ApiResponse {
  success: boolean
  timestamp: string
  total_files: number
  processed_files: number
  failed_files: number
  results?: ResultItem[]
  extraction_data?: ExtractedData[]
  renamed_files?: { [key: string]: string }
}

export default function PDFExtractorPage() {
  const [files, setFiles] = useState<FileList | null>(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<ApiResponse | null>(null)
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking")
  const { toast } = useToast()

  // Document type selection
  const [documentType, setDocumentType] = useState<string>("SKTT")

  const [useNameForRename, setUseNameForRename] = useState<boolean>(true)
  const [usePassportForRename, setUsePassportForRename] = useState<boolean>(true)
  const [enableFileRename, setEnableFileRename] = useState<boolean>(false)

  // Define API URL with fallback options
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://fermanta-pdf-extractor-api.hf.space"

  // Check API status on component mount
  useEffect(() => {
    const checkApiStatus = async () => {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000)

      try {
        const response = await fetch(`${API_URL}/health`, {
          method: "GET",
          headers: { Accept: "application/json" },
          mode: "cors",
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (response.ok) {
          setApiStatus("online")
          console.log("API is online:", API_URL)
        } else {
          console.warn("API responded but not ready:", response.status)
          setApiStatus("offline")
        }
      } catch (err) {
        clearTimeout(timeoutId)
        console.error("API connection error:", err)
        setApiStatus("offline")
      }
    }

    checkApiStatus()
  }, [API_URL])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files)
    setResults(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!files || files.length === 0) {
      toast({
        title: "Error",
        description: "Please select at least one PDF file",
        variant: "destructive",
      })
      return
    }

    if (apiStatus === "offline") {
      toast({
        title: "API Offline",
        description: "The API server appears to be offline. Please try again later.",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      Array.from(files).forEach((file) => {
        formData.append("files", file)
      })

      formData.append("document_type", documentType)

      // Choose endpoint based on file renaming option
      const endpoint = enableFileRename ? "/extract-with-rename" : "/extract"

      if (enableFileRename) {
        formData.append("use_name_for_rename", useNameForRename.toString())
        formData.append("use_passport_for_rename", usePassportForRename.toString())
      }

      console.log(`Sending request to: ${API_URL}${endpoint}`)
      console.log(`Document type: ${documentType}`)
      console.log(`Number of files: ${files.length}`)
      console.log(`File renaming enabled: ${enableFileRename}`)

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000)

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
        mode: "cors",
        headers: { Accept: "application/json" },
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorText = await response.text()
        console.error("API Error Response:", response.status, errorText)
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText || "No error details available"}`)
      }

      const data: ApiResponse = await response.json()

      // ✅ PERBAIKAN: Handle different response structures
      if (enableFileRename && data.extraction_data) {
        // Convert extraction_data to results format for consistent handling
        const convertedResults: ResultItem[] = data.extraction_data.map((extractedData, index) => ({
          filename: files[index]?.name || `File ${index + 1}`,
          status: "success" as const,
          data: extractedData,
        }))

        setResults({
          ...data,
          results: convertedResults,
        })
      } else {
        // Normal /extract response
        setResults(data)
      }

      toast({
        title: "Success",
        description: `Processed ${data.processed_files} out of ${data.total_files} files`,
      })
    } catch (error) {
      console.error("Fetch Error:", error)

      if (error instanceof TypeError && error.message.includes("Failed to fetch")) {
        toast({
          title: "Connection Error",
          description: "Could not connect to the API server. Please check your internet connection or try again later.",
          variant: "destructive",
        })
      } else if (error instanceof DOMException && error.name === "AbortError") {
        toast({
          title: "Request Timeout",
          description: "The request took too long to complete. Please try again or use smaller files.",
          variant: "destructive",
        })
      } else {
        toast({
          title: "Error",
          description: `Failed to extract text: ${error instanceof Error ? error.message : "Unknown error"}`,
          variant: "destructive",
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied",
      description: "Text copied to clipboard",
    })
  }

  const downloadAllAsJSON = () => {
    if (!results) return

    const element = document.createElement("a")
    const file = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" })
    element.href = URL.createObjectURL(file)
    element.download = `pdf_extraction_results_${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const downloadRenamedZip = async (retryCount = 0) => {
    console.log("=== ZIP DOWNLOAD ATTEMPT ===")
    console.log("Retry count:", retryCount)
    console.log("Results object:", results)
    
    if (!results) {
      toast({
        title: "Error",
        description: "No results available. Please process files first.",
        variant: "destructive",
      })
      return
    }

    // Check if download_links exists
    if (!results.download_links?.zip) {
      console.error("No download_links.zip found in results:", results)
      toast({
        title: "Error",
        description: "No ZIP download link available. Please try processing the files again.",
        variant: "destructive",
      })
      return
    }

    try {
      // Extract filename from download link (same pattern as Excel)
      const zipPath = results.download_links.zip
      const filename = zipPath.split('/').pop() || 'renamed_files.zip'
      const downloadUrl = `${API_URL}${zipPath}`
      
      console.log("Download details:")
      console.log("  ZIP path:", zipPath)
      console.log("  Filename:", filename)
      console.log("  Download URL:", downloadUrl)
      console.log("  File info:", results.file_info)
      
      // Add timeout and better error handling (same pattern as successful requests)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000) // 60 second timeout for ZIP
      
      console.log("Making fetch request...")
      const response = await fetch(downloadUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/zip, application/octet-stream, */*',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0',
        },
        mode: 'cors',
        credentials: 'omit',
        signal: controller.signal,
      })
      
      clearTimeout(timeoutId)
      
      console.log("Response received:")
      console.log("  Status:", response.status)
      console.log("  Status text:", response.statusText)
      console.log("  Headers:", Object.fromEntries(response.headers.entries()))
      
      console.log("Response status:", response.status)
      console.log("Response headers:", Object.fromEntries(response.headers.entries()))
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error("Response error text:", errorText)
        
        // If 404 and this is first retry, wait a moment and try again
        if (response.status === 404 && retryCount < 2) {
          console.log(`404 error, retrying in 3 seconds... (attempt ${retryCount + 1})`)
          await new Promise(resolve => setTimeout(resolve, 3000))
          return downloadRenamedZip(retryCount + 1)
        }
        
        throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`)
      }
      
      const contentType = response.headers.get('content-type')
      console.log("Content-Type:", contentType)
      
      const blob = await response.blob()
      console.log("Blob size:", blob.size, "bytes")
      
      if (blob.size === 0) {
        throw new Error("Downloaded file is empty")
      }
      
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast({
        title: "Download Complete",
        description: `ZIP file downloaded successfully (${(blob.size / 1024 / 1024).toFixed(2)} MB)`,
      })
    } catch (error) {
      console.error("ZIP download error:", error)
      
      let errorMessage = "Unknown error occurred"
      if (error instanceof DOMException && error.name === "AbortError") {
        errorMessage = "Download timed out. Please try again."
      } else if (error instanceof TypeError && error.message.includes("Failed to fetch")) {
        errorMessage = "Network error. Please check your connection."
      } else if (error instanceof Error) {
        errorMessage = error.message
      }
      
      // Show retry option for certain errors
      if (retryCount < 2 && (errorMessage.includes("404") || errorMessage.includes("Network"))) {
        toast({
          title: "Download Failed",
          description: `${errorMessage} Attempting retry...`,
          variant: "destructive",
        })
        await new Promise(resolve => setTimeout(resolve, 2000))
        return downloadRenamedZip(retryCount + 1)
      }
      
      toast({
        title: "Download Error",
        description: `Failed to download ZIP file: ${errorMessage}`,
        variant: "destructive",
      })
    }
  }

  const downloadAsExcel = () => {
    if (!results || !results.results) return

    const successfulResults = results.results.filter((r) => r.status === "success" && r.data)
    const excelData = successfulResults.map((result, index) => {
      const baseData = {
        No: index + 1,
        Filename: result.filename,
        "Document Type": result.data?.["Jenis Dokumen"] || documentType,
      }

      // Add fields based on document type
      if (documentType === "DKPTKA") {
        return {
          ...baseData,
          "Nama Pemberi Kerja": result.data?.["Nama Pemberi Kerja"] || "",
          Alamat: result.data?.["Alamat"] || "",
          "No Telepon": result.data?.["No Telepon"] || "",
          Email: result.data?.["Email"] || "",
          "Nama TKA": result.data?.["Nama TKA"] || "",
          "Tempat/Tanggal Lahir": result.data?.["Tempat/Tanggal Lahir"] || "",
          "Nomor Paspor": result.data?.["Nomor Paspor"] || "",
          Kewarganegaraan: result.data?.["Kewarganegaraan"] || "",
          Jabatan: result.data?.["Jabatan"] || "",
          "Lokasi Kerja": result.data?.["Lokasi Kerja"] || "",
          "Kode Billing Pembayaran": result.data?.["Kode Billing Pembayaran"] || "",
          DKPTKA: result.data?.["DKPTKA"] || "",
        }
      } else {
        return {
          ...baseData,
          Name: result.data?.Name || result.data?.["Nama TKA"] || "",
          "Place of Birth":
            result.data?.["Place of Birth"] || result.data?.["Place & Date of Birth"]?.split(",")[0] || "",
          "Date of Birth":
            result.data?.["Date of Birth"] ||
            result.data?.["Place & Date of Birth"]?.split(",")[1]?.trim() ||
            result.data?.["Tempat/Tanggal Lahir"] ||
            "",
          "Passport No":
            result.data?.["Passport No"] || result.data?.["Passport Number"] || result.data?.["Nomor Paspor"] || "",
          "Passport Expiry": result.data?.["Passport Expiry"] || "",
          "Date Issue": result.data?.["Date Issue"] || "",
          NIK: result.data?.NIK || "",
          Nationality: result.data?.Nationality || result.data?.Kewarganegaraan || "",
          Gender: result.data?.["Jenis Kelamin"] || result.data?.Gender || "",
          Address: result.data?.Address || result.data?.["Alamat Tempat Tinggal"] || "",
          Occupation: result.data?.Occupation || result.data?.Jabatan || "",
          "Permit Number": result.data?.["Permit Number"] || "",
          "Stay Permit Expiry": result.data?.["Stay Permit Expiry"] || "",
          "Nomor Keputusan": result.data?.["Nomor Keputusan"] || "",
          "Lokasi Kerja": result.data?.["Lokasi Kerja"] || "",
          Berlaku: result.data?.Berlaku || "",
        }
      }
    })

    // Convert to CSV format
    const headers = Object.keys(excelData[0] || {})
    const csvContent = [
      headers.join(","),
      ...excelData.map((row) => headers.map((header) => `"${row[header as keyof typeof row] || ""}"`).join(",")),
    ].join("\n")

    const element = document.createElement("a")
    const file = new Blob([csvContent], { type: "text/csv" })
    element.href = URL.createObjectURL(file)
    element.download = `Hasil_Ekstraksi_${documentType}_${new Date().toISOString().split("T")[0]}.csv`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)

    toast({
      title: "Excel Downloaded",
      description: "Extraction results have been downloaded as CSV file",
    })
  }

  const getTableColumns = () => {
    if (!results || !results.results || results.results.length === 0) return []

    const successfulResult = results.results.find((r) => r.status === "success" && r.data)
    if (!successfulResult?.data) return []

    switch (documentType) {
      case "SKTT":
        return [
          "Name",
          "NIK",
          "Place of Birth",
          "Date of Birth",
          "Gender",
          "Nationality",
          "Occupation",
          "Address",
          "KITAS/KITAP",
          "Passport Expiry",
          "Date Issue",
          "Document Type",
        ]
      case "EVLN":
        return [
          "Name",
          "Place of Birth",
          "Date of Birth",
          "Passport No",
          "Passport Expiry",
          "Date Issue",
          "Document Type",
        ]
      case "ITAS":
      case "ITK":
        return [
          "Name",
          "Permit Number",
          "Place & Date of Birth",
          "Passport Number",
          "Passport Expiry",
          "Nationality",
          "Gender",
          "Address",
          "Occupation",
          "Date Issue",
          "Document Type",
        ]
      case "Notifikasi":
        return [
          "Nomor Keputusan",
          "Nama TKA",
          "Tempat/Tanggal Lahir",
          "Kewarganegaraan",
          "Alamat Tempat Tinggal",
          "Nomor Paspor",
          "Jabatan",
          "Lokasi Kerja",
          "Berlaku",
          "Date Issue",
          "Document Type",
        ]
      case "DKPTKA":
        return [
          "Nama Pemberi Kerja",
          "Alamat",
          "No Telepon",
          "Email",
          "Nama TKA",
          "Tempat/Tanggal Lahir",
          "Nomor Paspor",
          "Kewarganegaraan",
          "Jabatan",
          "Lokasi Kerja",
          "Kode Billing Pembayaran",
          "DKPTKA",
          "Document Type",
        ]
      default:
        return [
          "Name",
          "Place of Birth",
          "Date of Birth",
          "Passport No",
          "Passport Expiry",
          "Date Issue",
          "Document Type",
        ]
    }
  }

  const getTableData = () => {
    if (!results || !results.results) return []

    return results.results
      .filter((r) => r.status === "success" && r.data)
      .map((result, index) => ({
        index,
        filename: result.filename,
        ...result.data,
      }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-32 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-32 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-500"></div>
      </div>
      
      <div className="max-w-7xl mx-auto space-y-8 relative z-10">
        {/* Modern Header */}
        <div className="text-center space-y-6 py-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-3 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20">
              <FileText className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent">
              LDB Document PDF
            </h1>
          </div>
          <p className="text-xl text-white/80 max-w-3xl mx-auto leading-relaxed">
            Transform your PDF documents with AI-powered extraction and intelligent file renaming
          </p>
          <div className="flex items-center justify-center space-x-6 text-sm text-white/60">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Secure Processing</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
              <span>Batch Upload</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
              <span>Smart Rename</span>
            </div>
          </div>
        </div>

        {/* API Status Indicator */}
        {apiStatus === "offline" && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>API Connection Error</AlertTitle>
            <AlertDescription>
              Cannot connect to the API server. The extraction service may be unavailable.
              <Button
                variant="outline"
                size="sm"
                className="ml-2 bg-transparent"
                onClick={() => window.location.reload()}
              >
                Retry Connection
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Upload Form */}
        <Card className="bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl hover:shadow-purple-500/10 transition-all duration-500 hover:bg-white/15">
          <CardHeader>
            <CardTitle className="flex items-center space-x-3 text-white text-xl">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Upload className="h-5 w-5 text-purple-300" />
              </div>
              <span className="bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">Upload PDF Files</span>
            </CardTitle>
            <CardDescription className="text-white/70 text-base">
              Select multiple PDF files for intelligent extraction and automated renaming
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="pdf-files">Choose PDF Files</Label>
                <Input
                  id="pdf-files"
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={handleFileChange}
                  className="cursor-pointer"
                />
                {files && files.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {Array.from(files).map((file, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="document-type">Document Type</Label>
                <select
                  id="document-type"
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="SKTT">SKTT</option>
                  <option value="EVLN">EVLN</option>
                  <option value="ITAS">ITAS</option>
                  <option value="ITK">ITK</option>
                  <option value="Notifikasi">Notifikasi</option>
                  <option value="DKPTKA">DKPTKA</option>
                </select>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="enable-rename"
                    checked={enableFileRename}
                    onChange={(e) => setEnableFileRename(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <Label htmlFor="enable-rename">Enable File Renaming</Label>
                </div>

                {enableFileRename && (
                  <div className="ml-6 space-y-2">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="use-name"
                        checked={useNameForRename}
                        onChange={(e) => setUseNameForRename(e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <Label htmlFor="use-name">Use Name in filename</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="use-passport"
                        checked={usePassportForRename}
                        onChange={(e) => setUsePassportForRename(e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <Label htmlFor="use-passport">Use Passport Number in filename</Label>
                    </div>
                  </div>
                )}
              </div>

              <Button
                type="submit"
                disabled={loading || !files || files.length === 0 || apiStatus === "offline"}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0 shadow-xl transform hover:scale-[1.02] transition-all duration-300 text-lg py-6"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Extracting Text...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Submit
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* Success Header */}
            <div className="flex items-center space-x-2 text-green-600">
              <CheckCircle className="h-6 w-6" />
              <h2 className="text-2xl font-bold">Proses Berhasil</h2>
            </div>

            {/* Enhanced Renamed Files Display with Download */}
            {results.renamed_files && (
              <Card className="bg-white/10 backdrop-blur-lg border border-white/20 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-white">
                    <div className="flex items-center space-x-2">
                      <FolderOpen className="h-5 w-5 text-green-400" />
                      <span>File Renaming Results</span>
                      <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
                        {Object.keys(results.renamed_files).length} files
                      </Badge>
                    </div>
                    <Button 
                      onClick={downloadRenamedZip}
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0 shadow-lg"
                      size="sm"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download ZIP
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(results.renamed_files).map(([original, renamed]) => (
                      <div key={original} className="flex justify-between items-center p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:bg-white/10 transition-all duration-300">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white/70 truncate">{original}</p>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <div className="w-6 h-0.5 bg-gradient-to-r from-purple-400 to-blue-400 rounded-full"></div>
                          <p className="text-sm font-medium text-white truncate max-w-xs">{renamed}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Tabs for different views */}
            <Tabs defaultValue="table" className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-white/10 backdrop-blur-lg border border-white/20 p-1">
                <TabsTrigger value="table" className="flex items-center space-x-2">
                  <FileSpreadsheet className="h-4 w-4" />
                  <span>Extraction Result</span>
                </TabsTrigger>
                <TabsTrigger value="excel" className="flex items-center space-x-2">
                  <Download className="h-4 w-4" />
                  <span>Excel File</span>
                </TabsTrigger>
                <TabsTrigger value="files" className="flex items-center space-x-2">
                  <FolderOpen className="h-4 w-4" />
                  <span>File Details</span>
                </TabsTrigger>
              </TabsList>

              {/* Table View */}
              <TabsContent value="table" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Extraction Result Data</CardTitle>
                    <CardDescription>
                      Processed {results.processed_files} out of {results.total_files} files successfully
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="w-12">No</TableHead>
                            <TableHead>Filename</TableHead>
                            {getTableColumns().map((column) => (
                              <TableHead key={column}>{column}</TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {getTableData().map((row, index) => (
                            <TableRow key={index}>
                              <TableCell>{index + 1}</TableCell>
                              <TableCell className="font-medium">{row.filename}</TableCell>
                              {getTableColumns().map((column) => (
                                <TableCell key={column}>{row[column as keyof typeof row] || "-"}</TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Excel Export */}
              <TabsContent value="excel" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Export to Excel</CardTitle>
                    <CardDescription>Download extraction results as Excel/CSV file</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="text-center p-6 bg-green-50 rounded-lg border border-green-200">
                        <FileSpreadsheet className="h-12 w-12 text-green-600 mx-auto mb-2" />
                        <h3 className="font-semibold text-green-800">Excel Format</h3>
                        <p className="text-sm text-green-600 mb-4">Download as CSV file (Excel compatible)</p>
                        <Button onClick={downloadAsExcel} className="w-full">
                          <Download className="mr-2 h-4 w-4" />
                          Download Excel
                        </Button>
                      </div>
                      <div className="text-center p-6 bg-blue-50 rounded-lg border border-blue-200">
                        <FileText className="h-12 w-12 text-blue-600 mx-auto mb-2" />
                        <h3 className="font-semibold text-blue-800">JSON Format</h3>
                        <p className="text-sm text-blue-600 mb-4">Download raw JSON data</p>
                        <Button onClick={downloadAllAsJSON} variant="outline" className="w-full bg-transparent">
                          <Download className="mr-2 h-4 w-4" />
                          Download JSON
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Individual File Results */}
              <TabsContent value="files" className="space-y-4">
                {results.results &&
                  results.results.map((result, index) => (
                    <Card key={index} className="shadow-md">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            {result.status === "success" ? (
                              <CheckCircle className="h-5 w-5 text-green-500" />
                            ) : (
                              <XCircle className="h-5 w-5 text-red-500" />
                            )}
                            <span className="truncate">File {result.filename}</span>
                          </div>
                          <Badge variant={result.status === "success" ? "default" : "destructive"}>
                            {result.status}
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {result.status === "success" && result.data ? (
                          <div className="space-y-4">
                            <div className="flex space-x-2">
                              <Button
                                onClick={() => copyToClipboard(JSON.stringify(result.data, null, 2))}
                                variant="outline"
                                size="sm"
                              >
                                <Copy className="mr-2 h-4 w-4" />
                                Copy Data
                              </Button>
                            </div>
                            <Separator />
                            <div className="space-y-2">
                              <Label>Extracted Data:</Label>
                              <div className="bg-gray-50 p-4 rounded-md border border-gray-200 overflow-auto max-h-[400px]">
                                <pre className="text-sm whitespace-pre-wrap">
                                  {JSON.stringify(result.data, null, 2)}
                                </pre>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-red-700 font-medium">Error:</p>
                            <p className="text-red-600 text-sm">{result.error}</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
              </TabsContent>
            </Tabs>
          </div>
        )}

        {/* Modern Footer */}
        <div className="text-center py-8">
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 max-w-md mx-auto">
            <p className="text-white/80 font-medium">Part Of Tools Laman Davindo Bahman</p>
            <div className="flex items-center justify-center space-x-2 mt-3">
              <span className="text-white/60">API Status:</span>
              <div className="flex items-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    apiStatus === "online" 
                      ? "bg-green-400 animate-pulse" 
                      : apiStatus === "offline" 
                      ? "bg-red-400" 
                      : "bg-yellow-400 animate-ping"
                  }`}
                ></div>
                <span
                  className={`font-semibold ${
                    apiStatus === "online" ? "text-green-300" : apiStatus === "offline" ? "text-red-300" : "text-yellow-300"
                  }`}
                >
                  {apiStatus === "online" ? "Online" : apiStatus === "offline" ? "Offline" : "Checking..."}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
