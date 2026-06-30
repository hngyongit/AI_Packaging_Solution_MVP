import React from 'react'
import { MessageSquarePlus, Package, TrendingUp, ShieldCheck, Clock } from 'lucide-react'

export default function EmptyState({ onNew }) {
    const features = [
        { icon: Package, title: 'Kích thước Thùng', desc: 'Nhận kích thước thùng tối ưu cho sản phẩm của bạn' },
        { icon: TrendingUp, title: 'Tối ưu Chi phí', desc: 'Giảm thiểu chi phí đóng gói với đề xuất thông minh' },
        { icon: ShieldCheck, title: 'An toàn Cấu trúc', desc: 'Đảm bảo bao bì đáp ứng các tiêu chuẩn an toàn' },
        { icon: Clock, title: 'Xử lý Nhanh', desc: 'Nhận tư vấn chuyên gia trong vài giây' },
    ]

    return (
        <div className="flex flex-col items-center justify-center h-full px-6">
            <div className="max-w-2xl mx-auto text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-carton-500 text-white mb-6">
                    <Package className="w-8 h-8" />
                </div>

                <h2 className="text-3xl font-bold text-carton-900 mb-3">
                    Giải pháp Bao bì AI
                </h2>

                <p className="text-base text-carton-600 max-w-md mx-auto mb-8">
                    Chuyên gia tư vấn bao bì của bạn về thiết kế, báo giá và tối ưu hóa thùng carton.
                </p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
                    {features.map((feature, i) => (
                        <div key={i} className="flex flex-col items-center text-center p-3 bg-pearl-100 border border-carton-200 hover:bg-carton-100 transition">
                            <feature.icon className="w-5 h-5 text-carton-600 mb-1.5" />
                            <span className="text-xs font-medium text-carton-800 leading-tight">
                                {feature.desc}
                            </span>
                        </div>
                    ))}
                </div>

                <button
                    onClick={onNew}
                    className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-carton-500 hover:bg-carton-600 text-white font-semibold transition"
                >
                    <MessageSquarePlus className="w-5 h-5" />
                    Bắt đầu trò chuyện mới
                </button>

                <p className="mt-6 text-xs text-carton-500">
                    Hỏi về thùng carton, báo giá, in ấn hoặc tối ưu hóa bao bì
                </p>
            </div>
        </div>
    )
}
