import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Camera, Palette, Save, Share2, ShoppingCart, ArrowLeft, Play, Heart, Download } from 'lucide-react'
import './App.css'

function App() {
  const [currentScreen, setCurrentScreen] = useState('splash')
  const [selectedProduct, setSelectedProduct] = useState('lipstick')
  const [selectedColor, setSelectedColor] = useState('#ff6b6b')
  const [intensity, setIntensity] = useState([50])

  const colors = {
    lipstick: ['#ff6b6b', '#ff4757', '#c44569', '#f8b500', '#ff3838'],
    eyeshadow: ['#a55eea', '#3742fa', '#2f3542', '#ff6348', '#ff9ff3'],
    blush: ['#ff9ff3', '#ff6b9d', '#ff7675', '#fd79a8', '#e84393']
  }

  const SplashScreen = () => (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-50 to-indigo-100 flex flex-col items-center justify-center p-6">
      <div className="text-center space-y-8">
        <div className="w-32 h-32 mx-auto bg-gradient-to-br from-pink-400 to-purple-500 rounded-3xl flex items-center justify-center shadow-2xl">
          <Camera className="w-16 h-16 text-white" />
        </div>
        <div className="space-y-4">
          <h1 className="text-4xl font-bold text-gray-800">GlowMirror</h1>
          <p className="text-xl text-gray-600 font-medium">جربي مكياجك قبل شرائه!</p>
        </div>
        <Button 
          onClick={() => setCurrentScreen('camera')}
          className="bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white px-8 py-3 text-lg rounded-full shadow-lg transform transition-all duration-200 hover:scale-105"
        >
          ابدئي الآن
        </Button>
      </div>
    </div>
  )

  const CameraScreen = () => (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('splash')}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h2 className="text-lg font-semibold">GlowMirror AR</h2>
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('gallery')}>
          <Heart className="w-5 h-5" />
        </Button>
      </div>

      {/* Camera View */}
      <div className="flex-1 relative bg-gray-200 m-4 rounded-2xl overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-pink-200 to-purple-200 flex items-center justify-center">
          <div className="text-center space-y-4">
            <Camera className="w-16 h-16 text-gray-500 mx-auto" />
            <p className="text-gray-600">كاميرا الوجه الحية</p>
          </div>
        </div>

        {/* AR Controls Overlay */}
        <div className="absolute bottom-4 left-4 right-4 space-y-4">
          {/* Product Categories */}
          <div className="flex justify-center space-x-4">
            {['lipstick', 'eyeshadow', 'blush'].map((product) => (
              <Button
                key={product}
                variant={selectedProduct === product ? "default" : "secondary"}
                size="sm"
                onClick={() => {
                  setSelectedProduct(product)
                  setCurrentScreen('productSelector')
                }}
                className="rounded-full"
              >
                <Palette className="w-4 h-4 mr-2" />
                {product === 'lipstick' ? 'أحمر شفاه' : product === 'eyeshadow' ? 'ظل عيون' : 'بلاشر'}
              </Button>
            ))}
          </div>

          {/* Color Palette */}
          <div className="flex justify-center space-x-2">
            {colors[selectedProduct].map((color) => (
              <button
                key={color}
                onClick={() => setSelectedColor(color)}
                className={`w-8 h-8 rounded-full border-2 ${selectedColor === color ? 'border-white shadow-lg scale-110' : 'border-gray-300'} transition-all duration-200`}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>

          {/* Intensity Slider */}
          <div className="bg-white/90 backdrop-blur-sm rounded-full p-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium">الكثافة</span>
              <Slider
                value={intensity}
                onValueChange={setIntensity}
                max={100}
                step={1}
                className="flex-1"
              />
              <span className="text-sm text-gray-600">{intensity[0]}%</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center space-x-4">
            <Button 
              onClick={() => setCurrentScreen('saveShare')}
              className="bg-green-500 hover:bg-green-600 text-white rounded-full"
            >
              <Save className="w-4 h-4 mr-2" />
              حفظ
            </Button>
            <Button 
              onClick={() => setCurrentScreen('purchase')}
              className="bg-blue-500 hover:bg-blue-600 text-white rounded-full"
            >
              <ShoppingCart className="w-4 h-4 mr-2" />
              شراء
            </Button>
          </div>
        </div>
      </div>
    </div>
  )

  const ProductSelectorScreen = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('camera')}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h2 className="text-lg font-semibold">اختيار المنتج</h2>
        <div></div>
      </div>

      <div className="p-6 space-y-6">
        {/* Product Categories */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { id: 'lipstick', name: 'أحمر شفاه', icon: '💄' },
            { id: 'eyeshadow', name: 'ظل عيون', icon: '👁️' },
            { id: 'blush', name: 'بلاشر', icon: '🌸' }
          ].map((product) => (
            <Card 
              key={product.id}
              className={`cursor-pointer transition-all duration-200 ${selectedProduct === product.id ? 'ring-2 ring-pink-500 bg-pink-50' : 'hover:shadow-md'}`}
              onClick={() => setSelectedProduct(product.id)}
            >
              <CardContent className="p-6 text-center">
                <div className="text-3xl mb-2">{product.icon}</div>
                <p className="font-medium">{product.name}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Color Grid */}
        <div>
          <h3 className="text-xl font-semibold mb-4 text-center">
            {selectedProduct === 'lipstick' ? 'أحمر شفاه' : selectedProduct === 'eyeshadow' ? 'ظل عيون' : 'بلاشر'}
          </h3>
          <div className="grid grid-cols-4 gap-4">
            {colors[selectedProduct].map((color, index) => (
              <button
                key={index}
                onClick={() => {
                  setSelectedColor(color)
                  setCurrentScreen('camera')
                }}
                className={`aspect-square rounded-full border-4 ${selectedColor === color ? 'border-white shadow-xl scale-110' : 'border-gray-200'} transition-all duration-200 hover:scale-105`}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  const SaveShareScreen = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('camera')}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h2 className="text-lg font-semibold">حفظ ومشاركة</h2>
        <div></div>
      </div>

      <div className="p-6 space-y-6">
        {/* Preview Image */}
        <Card className="overflow-hidden">
          <div className="aspect-square bg-gradient-to-br from-pink-200 to-purple-200 flex items-center justify-center">
            <div className="text-center space-y-2">
              <Camera className="w-12 h-12 text-gray-500 mx-auto" />
              <p className="text-gray-600">معاينة الصورة</p>
            </div>
          </div>
        </Card>

        {/* Save Button */}
        <Button className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-xl">
          <Download className="w-5 h-5 mr-2" />
          حفظ الصورة
        </Button>

        {/* Share Options */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-center">مشاركة على</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { name: 'TikTok', color: 'bg-black', icon: '🎵' },
              { name: 'Instagram', color: 'bg-gradient-to-r from-purple-500 to-pink-500', icon: '📷' },
              { name: 'Snapchat', color: 'bg-yellow-400', icon: '👻' },
              { name: 'WhatsApp', color: 'bg-green-500', icon: '💬' }
            ].map((platform) => (
              <Button
                key={platform.name}
                className={`${platform.color} text-white py-3 rounded-xl hover:opacity-90`}
              >
                <span className="mr-2">{platform.icon}</span>
                {platform.name}
              </Button>
            ))}
          </div>
        </div>

        <Button 
          variant="outline" 
          className="w-full py-3 rounded-xl"
          onClick={() => setCurrentScreen('camera')}
        >
          تجربة فلاتر إضافية
        </Button>
      </div>
    </div>
  )

  const PurchaseScreen = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('camera')}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h2 className="text-lg font-semibold">شراء المنتج</h2>
        <div></div>
      </div>

      <div className="p-6 space-y-6">
        {/* Product Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div 
                className="w-16 h-16 rounded-full border-2 border-gray-200"
                style={{ backgroundColor: selectedColor }}
              />
              <div className="flex-1">
                <h3 className="font-semibold text-lg">
                  {selectedProduct === 'lipstick' ? 'أحمر شفاه' : selectedProduct === 'eyeshadow' ? 'ظل عيون' : 'بلاشر'}
                </h3>
                <p className="text-gray-600">اللون المختار</p>
                <p className="text-xl font-bold text-green-600">99 ريال</p>
              </div>
              <Button className="bg-blue-500 hover:bg-blue-600 text-white">
                <ShoppingCart className="w-4 h-4 mr-2" />
                شراء الآن
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Payment Methods */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">طرق الدفع</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { name: 'STC Pay', icon: '📱' },
              { name: 'Apple Pay', icon: '🍎' },
              { name: 'Google Pay', icon: '🔵' },
              { name: 'بطاقة بنكية', icon: '💳' }
            ].map((method) => (
              <Button
                key={method.name}
                variant="outline"
                className="py-3 rounded-xl hover:bg-gray-50"
              >
                <span className="mr-2">{method.icon}</span>
                {method.name}
              </Button>
            ))}
          </div>
        </div>

        {/* Order Options */}
        <div className="space-y-3">
          <Button variant="outline" className="w-full py-3 rounded-xl">
            تأكيد الطلب
          </Button>
          <Button variant="outline" className="w-full py-3 rounded-xl">
            تتبع الشحنة
          </Button>
        </div>
      </div>
    </div>
  )

  const GalleryScreen = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('camera')}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h2 className="text-lg font-semibold">المعرض</h2>
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('recommendations')}>
          <Heart className="w-5 h-5" />
        </Button>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-2 gap-4">
          {Array.from({ length: 8 }, (_, i) => (
            <Card key={i} className="overflow-hidden">
              <div className="aspect-square bg-gradient-to-br from-pink-200 to-purple-200 flex items-center justify-center">
                <div className="text-center">
                  <Camera className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">إطلالة {i + 1}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )

  const RecommendationsScreen = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('gallery')}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h2 className="text-lg font-semibold">التوصيات</h2>
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('tutorials')}>
          <Play className="w-5 h-5" />
        </Button>
      </div>

      <div className="p-6 space-y-6">
        <div className="text-center space-y-2">
          <h3 className="text-xl font-semibold">موصى لك</h3>
          <p className="text-gray-600">ألوان ومنتجات مناسبة لبشرتك</p>
        </div>

        <div className="space-y-4">
          {[
            { name: 'أحمر شفاه وردي', price: '89 ريال', color: '#ff6b9d' },
            { name: 'ظل عيون ذهبي', price: '129 ريال', color: '#f8b500' },
            { name: 'بلاشر خوخي', price: '79 ريال', color: '#ff7675' }
          ].map((product, index) => (
            <Card key={index}>
              <CardContent className="p-4">
                <div className="flex items-center space-x-4">
                  <div 
                    className="w-12 h-12 rounded-full border-2 border-gray-200"
                    style={{ backgroundColor: product.color }}
                  />
                  <div className="flex-1">
                    <h4 className="font-medium">{product.name}</h4>
                    <p className="text-green-600 font-semibold">{product.price}</p>
                  </div>
                  <Button size="sm" className="bg-pink-500 hover:bg-pink-600 text-white">
                    جربي
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )

  const TutorialsScreen = () => (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => setCurrentScreen('recommendations')}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <h2 className="text-lg font-semibold">الفيديوهات التعليمية</h2>
        <div></div>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 gap-4">
          {[
            'مكياج طبيعي للمبتدئات',
            'تطبيق أحمر الشفاه المثالي',
            'ظل العيون المدخن',
            'كونتور الوجه الأساسي'
          ].map((title, index) => (
            <Card key={index} className="overflow-hidden">
              <div className="aspect-video bg-gradient-to-br from-pink-200 to-purple-200 flex items-center justify-center relative">
                <Play className="w-12 h-12 text-white bg-black/50 rounded-full p-3" />
                <div className="absolute bottom-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-sm">
                  {Math.floor(Math.random() * 10) + 5}:00
                </div>
              </div>
              <CardContent className="p-4">
                <h4 className="font-medium">{title}</h4>
                <p className="text-sm text-gray-600 mt-1">فيديو تعليمي</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )

  const renderScreen = () => {
    switch (currentScreen) {
      case 'splash': return <SplashScreen />
      case 'camera': return <CameraScreen />
      case 'productSelector': return <ProductSelectorScreen />
      case 'saveShare': return <SaveShareScreen />
      case 'purchase': return <PurchaseScreen />
      case 'gallery': return <GalleryScreen />
      case 'recommendations': return <RecommendationsScreen />
      case 'tutorials': return <TutorialsScreen />
      default: return <SplashScreen />
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white min-h-screen">
      {renderScreen()}
    </div>
  )
}

export default App

